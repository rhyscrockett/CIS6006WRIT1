import sqlite3 as sql
import random # generate unique ID
import os # generate key
import json # store the student credentials

os.environ["GOOGLE_APPLICATION_CREDENTIALS"]='natural-bison-345312-7f7a1bd41916.json'

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
            break
        elif selection == '2':
            view_record()
            break
        elif selection == '3':
            break
        else:
            print("Invalid Selection!")

def add_record():
    print("add: success")
    user_application_form()
    # TODO (1) appropriate password-less authentication to gain access to app
    # DONE - see brackets (2) a form that a user attaches credentials and submits -> user managment table (currently a dictionary; NO DATABASE)
    # DONE (3) after submitting form, app generates an encryption key and unique ID
    # DONE (4) display uniqiue ID and use either block/stream cipher to encrypt the file (credential(s)) and thus generate ciphertext
    # DONE (see below) (5) generate hash values of the ciphertext and unique ID
    # TODO (6) store the ciphertext in a cloud storage bucket
    # TODO (7) save the encryption key and hash values in a premised table -> user management table

def view_record():
    print("view: success")
    # TODO (1) user enters their unique ID
    # TODO (2) request to view/download/retrieve file
    # TODO (3) retrieves the hash values of unique ID from premised table  -> user managment table
    # TODO (4) app retrieves the ciphertext from the cloud storage bucket IF THE HASH VALUE MATCH
    # TODO (5) retrieves the encryption key associated with this unique ID
    # TODO (6) decrypts the ciphertext
    # TODO (7) performs file checksum and IF TRUE /
    # provides the file/record for viewing/downloading /
    # else file/record is corrupt and cannot be displayed/downloaded

def user_application_form():
    print("Please complete the form and submit to register:")
    credentials = {}
    credentials['first_name'] = input("What is your first name? ")
    credentials['last_name'] = input("What is your last name? ")
    credentials['email'] = input("What is your email address? ")
    creds = credentials.keys()
    for i in creds:
        print(f"{i.title()}: {credentials[i]}")
    rand = [random.randint(0, 9) for i in range(8)]
    gen_id = "st" + ''.join(map(str, rand))

    # Alternative ID generator
    #import uuid
    #gen_id2 = uuid.uuid4()
    #print(gen_id2)

    while True:
        submit = input("Check your details are correct and (s)ubmit. Alternatively, (e)xit: ").lower().strip()
        if submit == 's':
            # Write the json file
            with open(gen_id+".json", "w") as write_file:
                json.dump(credentials, write_file)
            break
        elif submit == 'e':
            break
        else:
            print("Invalid Selection!")

    print("Unique ID: ", gen_id, "(Do not lose this!)")
    from cryptography.fernet import Fernet
    key = Fernet.generate_key()
    print("Generated Key: ", key)
    f = Fernet(key)

    # load file 
    with open(gen_id+".json", "rb") as read_file:
        file_data = read_file.read()
        
    encrypted_data = f.encrypt(file_data) # encrypt the credentials

    print("Ciphertext>>>", encrypted_data) # ciphertext

    # write the encrypted data back to the same json file
    with open(gen_id+".json", "wb") as encrypt_file:
        encrypt_file.write(encrypted_data)

    # hashing example
    import hashlib
    #import binascii
    #text = 'hello'
    #data = text.encode("utf-8")
    #sha256hash = hashlib.sha256(data).digest()
    #print("SHA-256: ", binascii.hexlify(sha256hash))

    # Generate Hash Values

    # one hash value
    dk = hashlib.sha256()
    unique_id = gen_id.encode('utf-8') # convert to bytes
    dk.update(encrypted_data) # already bytes
    dk.update(unique_id)
    print("Generated Hash (both ID and encrypted data): ", dk.hexdigest())

    # two hash values
    cipher_hash = hashlib.sha256()
    id_hash = hashlib.sha256()
    cipher_hash.update(encrypted_data)
    id_hash.update(gen_id.encode("utf-8"))
    print("Ciphertext hash: ", cipher_hash.hexdigest())
    print("ID hash: ", id_hash.hexdigest())

    

def user_managment_table():
    con = sql.connect("database") # create a database
    c = con.cursor() # control the db

    #c.execute("""
    #CREATE TABLE IF NOT EXISTS students
    #([student_id] INTEGER PRIMARY KEY, [first_name] TEXT,
    #[last_name] TEXT, [email] VARCHAR)
    #""")

    #c.execute("""
    #INSERT INTO students (name,

    c.execute("""
    CREATE TABLE IF NOT EXISTS keys
    ([unique_id] INTEGER PRIMARY KEY, [encryption_key] TEXT,
    [hash_values] TEXT)
    """)

    con.commit() # save table
    
def main():
    #user_application_form()
    user_managment_table() # database
    app_menu() # start menu
    
    # TODO needed SQL "on premise" user access management table
    
if __name__ == '__main__':
    main()
