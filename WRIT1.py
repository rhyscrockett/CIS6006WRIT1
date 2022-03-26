import sqlite3 as sql

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
    # TODO (2) a form that a user attaches credentials and submits -> user managment table
    # TODO (3) after submitting form, app generates an encryption key and unique ID
    # TODO (4) display uniqiue ID and use either block/stream cipher to encrypt the file (credential(s)) and thus generate ciphertext
    # TODO (5) generate hash values of the ciphertext and unique ID
    # TODO (6) store the ciphertext in a cloud storage bucket
    # TODO (7) save the encryption key and hash value in a premised table -> user management table

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
    credentials['email'] = input("What is your email addres? ")
    creds = credentials.keys()
    for i in creds:
        print(f"{i}: {credentials[i]}")

    import random
    gen_id = [random.randint(0, 9) for i in range(8)]
    id = ''.join(map(str, gen_id))
    id = ("st") + id

    while True:
        submit = input("Check your details are correct and then press 's' to submit. Otherwise press 'e' to exit: ").lower().strip()
        if submit == 's':
            import json
            filename = open(id+".json", "w")
            json.dump(credentials, filename)
            filename.close()
            break
        elif submit == 'e':
            break
        else:
            print("Invalid Selection!")

    print("Unique ID: ",id, "(Do not lose this!)")
    
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
