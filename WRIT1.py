import sqlite3 as sql # premised storage
import random # generate unique ID
import os # generate key
import json # store the student credentials
import sys # for perfmoring exits
from cryptography.fernet import Fernet # encryption (AES, CBC MODE)
import boto3 # aws cloud storage
import hashlib # hashing

def app_menu():
    """The main menu of the application. Gets input from a user to create, view or exit the application."""
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
    """Allow the user to create a new account and credentials."""
    print("add: success") # test
    i = user_application_form() # run the user_application_form function and save the generated ID as g when successful
    k = generate_encryption_key() # run the generate_encryption_key function and save the generated key as f
    ct = encryption(i, k) # perform the encryption using the credentials (reading them from dir using ID) from user_application_form and the generated key from generate_encryption_key
    ct_hash = hashing(ct) # perform hashing for ciphertext (ciphertext already encoded)
    id_hash = hashing(i.encode("utf-8")) # perform hashing for unique ID (must be encoded before hashing)
    aws_cloud_storage_upload(i, ct) # upload the encrypted credentials to the cloud using the unique ID as the filename
    conn = establish_connection() # establish connection with a premised database
    create_user_management_table(conn) # create a user management table
    insert_data(conn, k, ct_hash, id_hash) # insert enc key, cipher has and ID hash into table (will check if already exists)
    
    # TODO (1) appropriate password-less authentication to gain access to app

def view_record():
    """Present the user with a menu to start record recovery."""
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
            k = credential_check(user_id)
            pt = decryption(user_id, k)
            checksum(user_id)
            return_credentials(user_id, pt)
            break
        elif selection == '2':
            print("End Process")
            break
        else:
            print("Invalid Selection!")

def credential_check(unique_id):
    """Perform hash checks between user ID and the ciphertext to ensure credentials are correct."""
    user_hash = hashing(unique_id.encode("utf-8")) # call hashing function on ID passed (must be encoded)
    
    connection = establish_connection() # connect to database
    c = connection.cursor() # create cursor to query search

    # check user id hash is present in premised storage
    param = user_hash.hexdigest() # create a parameter to seach for the matching hash
    results = c.execute("SELECT * FROM keys WHERE id_hash = ?", [param]) # search
    if results is None:
        print("User does not exist")
        sys.exit(1)
    else: # if id hash matches student input, retrieve the ciphertext from cloud
        aws_cloud_storage_download(unique_id) # run download function

    # retrieve encryption key associated with unique ID if hash match
    results = c.execute("SELECT encryption_key FROM keys WHERE id_hash = ?", [param]).fetchone()
    if results is None:
        print("Error recovering encryption key...")
        sys.exit(1)
    else:
        key = results[0] # return string of the encryption key
        c.close()

    return key

def aws_cloud_storage_download(file_name):
    """Downloads student credentials from AWS cloud storage bucket."""
    s3 = boto3.client("s3")
    bucket_name = "cis6006-storage"
    s3.download_file(bucket_name, file_name, file_name) # download the file from the relevant bucket and using the filename as a search
    print("\nDownloading...")

    print("Download successful!...\n")

def decryption(unique_id, key):
    """Decrypts the student credentials using the encryption key retrieved from credential_check()."""

    file_data = read_as_bytes(unique_id) # read the encrypted file as bytes

    f = Fernet(key) # to use the encryption key

    plaintext = f.decrypt(file_data) # decrypt the ciphertext back to plaintext

    return plaintext

def checksum(file_name):
    """Perform a file CHECKSUM using the hash generated with the ciphertext before uploading to the cloud."""
    connection = establish_connection()
    c = connection.cursor()

    file_data = read_as_bytes(file_name) # read the encrypted file as bytes to perform CHECKSUM
        
    # generate hash for downloaded file
    user_hash = hashing(file_data) # call the hashing function on the encoded ciphertext via cloud storage

    ## this should be used as the checksum isntead
    param = user_hash.hexdigest() # get str of user_hash
    results = c.execute("SELECT * FROM keys WHERE cipher_hash = ?", [param]) # search for matching hash
    if results is None:
        print("File/record is corrupt and therefore cannot be displayed/downloaded. Exiting...")
        print("Deleting downloaded copy...\n")
        os.remove(filename+".json") # removes the file from the dir
        sys.exit(1) # exit system
    else:
        print("CHECKSUM succesful")
        c.close()
        os.remove(file_name)
        # continue to return_credentials via view_record

def open_json(file_name):
    """Open JSON file."""
    with open(file_name+".json") as read_file:
        file_data = json.load(read_file)

    return file_data

def write_json(file_name, credentials):
    """Write JSON file."""
    with open(file_name+".json", "w") as data:
        json.dump(credentials, data) # save the dict credentials to a JSON file with the ID num as name

def read_as_bytes(file_name):
    """Read a non JSON file as bytes. Used in decryption and CHECKSUM."""
    with open(file_name, "rb") as read_file:
        file_data = read_file.read()

    return file_data

def return_credentials(filename, plaintext):
    """Upon successful CHECKSUM, offer the user to view or download the decrypted credentials.
    view prints the decrypted file using a dictionary, download keeps the decrypted json in the users dir."""
    json_string = json.loads(plaintext.decode("utf-8")) # loads the plaintext into string
    write_json(filename, json_string) # write string back to file which provides a py dictionay
    choice = input("Would you like to (v)iew or (d)ownload your credentials? ").strip().lower()
    while True:
        if choice == 'v':
            credentials = open_json(filename)
            print("First_Name:", credentials['first_name'])
            print("Last_Name:", credentials['last_name'])
            print("Email: ", credentials['email'])
            print("Deleting downloaded copy...\n")
            os.remove(filename+".json")
            break
        elif choice == 'd':
            print("Saving decrypted file to current directory...") # exit without deleting document
            break
        else:
            print("Incorrect input")
            continue
        
def generate_id():
    """Generates a unique ID to be used by a student."""
    rand = [random.randint(0, 9) for i in range(8)] # generate 8 random numbers (0, 9)
    gen_id = "st" + ''.join(map(str, rand)) # append st to the start, creating st(8 random nums)

    return gen_id

def generate_encryption_key():
    """Generate an encryption key using the cryptography library (Fernet - an AES CBC MODE based cipher)."""
    key = Fernet.generate_key()

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
            # write the credentials (python dictionary) to JSON file
            with open(unique_id+".json", "w") as data:
                json.dump(credentials, data) # save the dictionary credentials to a JSON file with the ID num as name
            break
        elif submit == 'e':
            print("Exiting...")
            sys.exit(1)
        else:
            print("Invalid Selection!")
    print("Unique ID: ", unique_id, "(Do not lose this!)")

    return unique_id

def encryption(unique_id, key):
    """Performs encryption on the user credentials JSON file using the generated key."""
    file_data = open_json(unique_id) # open JSON file which provides a py dictionary
    file_string = json.dumps(file_data) # convert the json dictionary python obj to python str
    encoded_string = file_string.encode("utf-8") # encode the str obj to bytes
    
    f = Fernet(key) # to use the encryption key
        
    encrypted_data = f.encrypt(encoded_string) # encrypt the credentials using the encryption key
    
    os.remove(unique_id+".json") # removes the credential file after encrypting

    return encrypted_data

def hashing(data):
    """Hashing function to create a sha256 hash."""
    hash_value = hashlib.sha256() # create sha256 hash object
    hash_value.update(data) # update the hash with the input data

    return hash_value # return the hash value

def aws_cloud_storage_upload(filename, encrypted_data):
    """Creates default Bucket for AWS to use. And uploads encrypted user credentials to as an object."""
    # create an S3 client
    s3 = boto3.client("s3")
    bucket_name = 'cis6006-storage'

    # Create a bucket called 'cis6006-storage
    s3.create_bucket(Bucket=bucket_name)

    # write the encrypted string of bytes (write_as_bytes)
    with open(filename, "wb") as encrypt_file:
        encrypt_file.write(encrypted_data)

    # Uploads the given file using a managed uploader, which will split
    # up large parts automatically and upload parts in parallel
    s3.upload_file(filename, bucket_name, filename)
    print("\nUploading...")

    # prints all objects (files) in bucket
    s3_resource = boto3.resource("s3")
    s3_bucket = s3_resource.Bucket(bucket_name)
    for obj in s3_bucket.objects.all():
        print(f"-- {obj.key}")

    print("Upload successful!...\n")

    print("Deleting local copy...\n")
    os.remove(filename) # removes the encrypted credentials file from the dir

def establish_connection():
    """Connect to the local table defined below. Used throughout the body of code."""
    connection = None
    try:
        connection = sql.connect("premised_table.db")
        print("Connected to database...\n")
        return connection
    except sql.Error as e:
        print(e)
    return connection

def create_user_management_table(connection):
    """Create a table on local storage. This will only need to be done once."""
    if connection is not None:
        c = connection.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS keys
        ([encryption_key] TEXT, [cipher_hash] TEXT, [id_hash] TEXT)
        """)
        c.close()
    else:
        print("Cannot connect to the database...\n")

def insert_data(connection, encryption_key, cipher_hash, id_hash):
    """Insert data (encryption key, ciphertext hash and ID hash into the premised table."""
    if connection is not None:
        c = connection.cursor()
        c.execute("""
        INSERT INTO keys (encryption_key, cipher_hash, id_hash) VALUES (?, ?, ?);
        """, (encryption_key.decode(), cipher_hash.hexdigest(), id_hash.hexdigest()))
        connection.commit() # save the table
        c.close()
    else:
        print("Cannot connect to the database...")
    
def main():
    app_menu() # start menu
    
if __name__ == '__main__':
    main()
