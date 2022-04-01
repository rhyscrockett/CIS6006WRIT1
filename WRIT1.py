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
    create_table(conn) # create a user managment table
    insert_data(conn, k, ct_hash, id_hash)
    #user_managment_table(k, ct_hash, id_hash) # database access and saving details
    
    # TODO (1) appropriate password-less authentication to gain access to app
    # DONE - see brackets (2) a form that a user attaches credentials and submits -> user managment table (currently a dictionary; NO DATABASE)
    # DONE (3) after submitting form, app generates an encryption key and unique ID
    # DONE (4) display uniqiue ID and use either block/stream cipher to encrypt the file (credential(s)) and thus generate ciphertext
    # DONE (5) generate hash values of the ciphertext and unique ID
    # DONE (6) store the ciphertext in a cloud storage bucket
    # DONE (7) save the encryption key and hash values in a premised table -> user management table

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
            
    # DONE (1) user enters their unique ID
    # DONE (2) request to view/download/retrieve file
    # DONE (3) retrieves the hash values of unique ID from premised table  -> user managment table
    # DONE (4) app retrieves the ciphertext from the cloud storage bucket IF THE HASH VALUE MATCH
    # DONE (5) retrieves the encryption key associated with this unique ID
    # (search for encryption key associated with id_hash)
    # DONE (6) decrypts the ciphertext
    # DONE (7) performs file checksum and IF TRUE /
    # provides the file/record for viewing/downloading /
    # else file/record is corrupt and cannot be displayed/downloaded

def credential_check(unique_id):
    """Perform hash checks between user ID and the ciphertext to ensure credentials are correct."""
    user_hash = hashing(unique_id.encode("utf-8")) # call the hashing function on the ID passed via view records (must be encoded)
    #print("Unique ID Hash: ", user_hash.hexdigest())

    connection = sql.connect("premised_table.db") # create a database
    c = connection.cursor() # control the db
    print("Connected to premised_table\n") # confirmation message

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

    return key

def aws_cloud_storage_download(file_name):
    """Downloads student credentials from AWS cloud storage bucket."""
    s3 = boto3.client("s3")
    file_name = file_name+".json"
    bucket_name = "cis6006-storage"
    s3.download_file(bucket_name, file_name, file_name) # download the file from the relevant bucket and using the filename as a search
    print("\nDownloading...")

    print("Download successful!...\n")

def decryption(unique_id, key):
    """Decrypts the student credentials using the encryption key retrieved from credential_check()."""
    # load file to bytes in order to decrypt data
    with open(unique_id+".json", "rb") as read_file:
        file_data = read_file.read() # read the file to file_data

    f = Fernet(key) # to use the encryption key

    # decrypted data waiting for successful checksum of hash
    plaintext = f.decrypt(file_data)

    return plaintext

def checksum(filename):
    """Perform a file CHECKSUM using the hash generated with the ciphertext before uploading to the cloud."""
    connection = sql.connect("premised_table.db") # create a database
    c = connection.cursor() # control the db
    print("Connected to premised_table\n") # confirmation message
    
    # load file to bytes in order to perform hashing
    with open(filename+".json", "rb") as read_file:
        file_data = read_file.read() # read the file to file_data
        
    # generate hash for downloaded file
    user_hash = hashing(file_data) # call the hashing function on the ciphertext via cloud storage (already encoded)

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
        # continue to return_credentials via view_record

def return_credentials(filename, plaintext):
    """Upon successful CHECKSUM, offer the user to view or download the decrypted credentials.
    view prints the decrypted file using a dictionary, download keeps the decrypted json in the users dir."""
    with open(filename+".json", "w") as write_file:
        write_file.write(plaintext.decode("utf-8")) # save the credentials using write to save the plaintext json string as a json formatted file
    choice = input("Would you like to (v)iew or (d)ownload your credentials? ").strip().lower()
    while True:
        if choice == 'v':
            with open(filename+".json") as json_file:
                credentials = json.load(json_file) # open json file to write the data to a python dictionary
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
    #print("Generated Key: ", key)

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
    """Performs encryption on the user credentials using the generated key for the unique ID."""
    # load file to bytes in order to encrypt data
    with open(unique_id+".json", "rb") as read_file:
        file_data = read_file.read() # read the file to file_data

    f = Fernet(key) # to use the encryption key
        
    encrypted_data = f.encrypt(file_data) # encrypt the credentials using the encryption key
    #print("Ciphertext >>>", encrypted_data) # print ciphertext

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
    print("\nUploading...")

    # prints all objects (files) in bucket
    s3_resource = boto3.resource("s3")
    s3_bucket = s3_resource.Bucket(bucket_name)
    for obj in s3_bucket.objects.all():
        print(f"-- {obj.key}")

    print("Upload successful!...\n")

    print("Deleting local copy...\n")
    os.remove(filename_id) # removes the file from the dir

    # delete objects from bucket
    #s3_bucket.objects.filter(Prefix='st17010024.json').delete() (UNCOMMENT AND ADJUST PREFIX TO DELETE)
    #s3_bucket.objects.all().delete() # delte all files in bucket

def user_managment_table(encryption_key, cipher_hash, id_hash):
    """Function to create a on-site premsed database, then create a table to hold the encryption key, ciphertext hash, and ID hash."""
    connection = sql.connect("premised_table.db") # create a database
    c = connection.cursor() # control the db
    print("Connected to premised_table\n") # confirmation message

    # command to create database
    c.execute("""
    CREATE TABLE IF NOT EXISTS keys
    ([unique_id] TEXT PRIMARY KEY, [encryption_key] TEXT, [cipher_hash] TEXT, [id_hash] TEXT)
    """)

    # command to insert into database
    c.execute("""
    INSERT INTO keys (encryption_key, cipher_hash, id_hash) VALUES (?, ?, ?);
    """, (encryption_key.decode(), cipher_hash.hexdigest(), id_hash.hexdigest()))
    
    ## loop to print all
    c.execute("SELECT * FROM keys")
    records = c.fetchall()
    for row in records:
        print(row)
    
    connection.commit() # save table
    print("Python Variables passed from parameters inserted successfully into sqlite\n") # success print

    c.close() # close database (memory managment)

def establish_connection():
    """Create's a new database """
    connection = None
    try:
        connection = sql.connect("premised_table.db")
        print("Connected to database...\n")
        print(sql.version)
        return connection
    except sql.Error as e:
        print(e)
    return connection

def create_table(connection):
    """Create a table on local storage. This will only need to be done once."""
    #connection = create_connection()
    if connection is not None:
        c = connection.cursor()
        c.execute("""
        CREATE TABLE IF NOT EXISTS keys
        ([encryption_key] TEXT, [cipher_hash] TEXT, [id_hash] TEXT)
        """)
    else:
        print("Cannot connect to the database...\n")
        

def insert_data(connection, encryption_key, cipher_hash, id_hash):
    """Insert data (encryption key, ciphertext hash and ID hash into the premised table."""
    #connection = create_connetion() # connect to database
    if connection is not None:
        c = connection.cursor()
        c.execute("""
        INSERT INTO keys (encryption_key, cipher_hash, id_hash) VALUES (?, ?, ?);
        """, (encryption_key.decode(), cipher_hash.hexdigest(), id_hash.hexdigest()))
        connection.commit() # save the table?
    else:
        print("Cannot connect to the database...")
    
def main():
    app_menu() # start menu
    
if __name__ == '__main__':
    main()
