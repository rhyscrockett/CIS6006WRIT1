import sqlite3 as sql
import random # generate unique ID
import os # generate key
import json # store the student credentials
import sys # for perfmoring exits
from cryptography.fernet import Fernet # encryption (AES, CBC MODE)
import boto3 # aws cloud storage
import hashlib # hashing

def app_menu():
    menu = {} # dictionary to hold selection with button
    menu['1'] = "Add Student Record: " # string 1 returns add student rec
    menu['2'] = "View/Retrieve Record: " # string 2 returns view rec
    menu['3'] = "Exit: " # string 3 returns exit
    while True:
        options = menu.keys() # return the keys from menu dictionary
        for entry in options:
            print(entry, menu[entry]) # print number alongside the text

        # allow user input for selecting the menu
        selection = input("Please select: ")
        if selection == '1':
            add_record()
            continue
        elif selection == '2':
            view_record()
            break
        elif selection == '3':
            break
        else:
            print("Invalid Selection!")

def add_record():
    print("add: success") # test
    i = user_application_form() # run the user_application_form function and save the generated ID as g when successful
    k = generate_encryption_key() # run the generate_encryption_key function and save the generated key as f
    ct = encryption(i, k) # perform the encryption using the credentials (reading them from dir using ID) from user_application_form and the generated key from generate_encryption_key
    ct_hash = hashing(ct) # perform hashing for ciphertext (ciphertext already encoded)
    id_hash = hashing(i.encode("utf-8")) # perform hashing for unique ID (must be encoded before hashing)
    aws_cloud_storage_upload(i, ct) # upload the encrypted credentials to the cloud using the unique ID as the filename
    user_managment_table(k, ct_hash, id_hash) # database access and saving details
    
    # TODO (1) appropriate password-less authentication to gain access to app
    # DONE - see brackets (2) a form that a user attaches credentials and submits -> user managment table (currently a dictionary; NO DATABASE)
    # DONE (3) after submitting form, app generates an encryption key and unique ID
    # DONE (4) display uniqiue ID and use either block/stream cipher to encrypt the file (credential(s)) and thus generate ciphertext
    # DONE (5) generate hash values of the ciphertext and unique ID
    # DONE (6) store the ciphertext in a cloud storage bucket
    # DONE (7) save the encryption key and hash values in a premised table -> user management table

def view_record():
    print("view: success")
    user_id = input("Enter your unique ID to continue: ")
    # do checks to ensure valid length and st at start etc)
    request = {}
    request['1'] = "Retrieve/download file: "
    request['2'] = "Exit: "
    while True:
        options = request.keys() # return the keys from menu dictionary
        for entry in options:
            print(entry, request[entry]) # print number alongside the text

        # allow user input for selecting the menu
        selection = input("Please select: ")
        if selection == '1':
            print("Start Process")
            check = credential_check(user_id)
            break
        elif selection == '2':
            print("End Process")
            break
        else:
            print("Invalid Selection!")
            
    # DONE (1) user enters their unique ID
    # DONE (2) request to view/download/retrieve file
    # DONE (3) retrieves the hash values of unique ID from premised table  -> user managment table
    # TODO (4) app retrieves the ciphertext from the cloud storage bucket IF THE HASH VALUE MATCH
    # TODO (5) retrieves the encryption key associated with this unique ID
    # TODO (6) decrypts the ciphertext
    # TODO (7) performs file checksum and IF TRUE /
    # provides the file/record for viewing/downloading /
    # else file/record is corrupt and cannot be displayed/downloaded

def credential_check(unique_id):
    """Perform hash checks between user ID and the ciphertext to ensure credentials are correct."""
    user_hash = hashing(unique_id.encode("utf-8")) # call the hashing function on the ID passed via view records (must be encoded)
    print("Unique ID Hash: ", user_hash.hexdigest())

    connection = sql.connect("premised_table.db") # create a database
    c = connection.cursor() # control the db
    print("\nConnected to premised_table\n") # confirmation message

    parameter = user_hash.hexdigest() # create a parameter to seach for the matching hash
    results = c.execute("SELECT * FROM keys WHERE id_hash = ?", [parameter]) # search
    if results is None:
        print("User does not exist")
        sys.exit(1)
    else:
        filename = unique_id+".json"
        s3 = boto3.client("s3")
        s3.download_file('cis6006-storage', filename, filename)
        print("Success")

    with open(unique_id+".json", "rb") as read_file:
        file_data = read_file.read() # read the file to file_data

    user_hash = hashing(file_data) # call the hashing function on the ciphertext via cloud storage (already encoded)
    print("Ciphertext Hash: ", user_hash.hexdigest()) # print hash

    parameter = user_hash.hexdigest() # get str of user_hash
    results = c.execute("SELECT * FROM keys WHERE cipher_hash = ?", [parameter]) # search for matching hash
    if results is None:
        print("Error recovering credentials") # if not matching hash is found, error is found
        sys.exit(1) # exit system
    else:
        print("Success") # else hash is found for ciphertext, continue with decryption
        
def generate_id():
    """Generates a unique ID to be used by a student."""
    rand = [random.randint(0, 9) for i in range(8)] # generate 8 random numbers (0, 9)
    gen_id = "st" + ''.join(map(str, rand)) # append st to the start, creating st(8 random nums)

    # Alternative ID generator
    #import uuid
    #gen_id2 = uuid.uuid4()
    #print(gen_id2)

    return gen_id

def generate_encryption_key():
    """Generate an encryption key using the cryptography library (Fernet - an AES CBC MODE based cipher)."""
    key = Fernet.generate_key()
    print("Generated Key: ", key)

    return key

def user_application_form():
    """A simple dictionary to hold a temporary form for the user to register. This form will be encrypted and stored in the cloud"""
    print("Please complete the form and submit to register:")
    credentials = {}
    credentials['first_name'] = input("What is your first name? ")
    credentials['last_name'] = input("What is your last name? ")
    credentials['email'] = input("What is your email address? ")
    creds = credentials.keys()
    for i in creds:
        print(f"{i.title()}: {credentials[i]}")

    while True:
        submit = input("Check your details are correct and (s)ubmit. Alternatively, (e)xit: ").lower().strip()
        if submit == 's':
            unique_id = generate_id() # generate a unique id
            # Write the json file
            with open(unique_id+".json", "w") as write_file:
                json.dump(credentials, write_file) # save the credentials to a JSON file with the ID num as name
            break
        elif submit == 'e':
            print("Exiting...")
            sys.exit(1)
        else:
            print("Invalid Selection!")
    print("Unique ID: ", unique_id, "(Do not lose this!)")

    return unique_id

def encryption(unique_id, key):
    # load file to bytes in order to encrypt data
    with open(unique_id+".json", "rb") as read_file:
        file_data = read_file.read() # read the file to file_data

    f = Fernet(key) # to use the encryption key
        
    encrypted_data = f.encrypt(file_data) # encrypt the credentials using the encryption key
    print("Ciphertext >>>", encrypted_data) # print ciphertext

    return encrypted_data

def hashing(data):
    hash_value = hashlib.sha256() # create sha256 hash object
    hash_value.update(data) # update the hash with the input data

    return hash_value # return the hash value

def aws_cloud_storage_upload(filename, encrypted_data):
    """Creates default Bucket for AWS to use."""
    # create an S3 client
    s3 = boto3.client("s3")

    # Create a bucket called 'cis6006-storage
    s3.create_bucket(Bucket='cis6006-storage')

    filename_id = filename+".json"

    #write the encrypted data back to the same json file
    with open(filename_id, "wb") as encrypt_file:
        encrypt_file.write(encrypted_data)

    bucket_name = 'cis6006-storage'

    # Uploads the given file using a managed uploader, which will split
    # up large parts automatically and upload parts in parallel
    s3.upload_file(filename_id, bucket_name, filename_id) #(UNCOMMENT TO UPLOAD FILES)

    # prints all objects (files) in bucket
    s3_resource = boto3.resource("s3")
    s3_bucket = s3_resource.Bucket(bucket_name)
    for obj in s3_bucket.objects.all():
        print(f"-- {obj.key}")

    print("Deleting the local copy...")
    os.remove(filename_id) # removes the file from the dir

    # delete objects from bucket
    #s3_bucket.objects.filter(Prefix='st17010024.json').delete() (UNCOMMENT AND ADJUST PREFIX TO DELETE)
    #s3_bucket.objects.all().delete() # delte all files in bucket

def user_managment_table(encryption_key, cipher_hash, id_hash):
    connection = sql.connect("premised_table.db") # create a database
    c = connection.cursor() # control the db
    print("\nConnected to premised_table\n") # confirmation message

    # command to create database
    c.execute("""
    CREATE TABLE IF NOT EXISTS keys
    ([unique_id] TEXT PRIMARY KEY, [encryption_key] TEXT, [cipher_hash] TEXT, [id_hash] TEXT)
    """)

    # command to insert into database
    c.execute("""
    INSERT INTO keys (encryption_key, cipher_hash, id_hash) VALUES (?, ?, ?);
    """, (encryption_key.decode(), cipher_hash.hexdigest(), id_hash.hexdigest()))

    #c.execute("DELETE FROM keys")
    
    ## loop to print all
    c.execute("SELECT * FROM keys")
    records = c.fetchall()
    for row in records:
        print(row)
    
    connection.commit() # save table
    print("\nPython Variables passed from parameters inserted successfully into sqlite\n") # success print

    c.close() # close database (memory managment)
    
def main():
    app_menu() # start menu
    
    # TODO needed SQL "on premise" user access management table
    
if __name__ == '__main__':
    main()
