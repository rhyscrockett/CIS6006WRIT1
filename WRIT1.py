
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
    # TODO (1) appropriate password-less authentication to gain access to app
    # TODO (2) a form that a user attaches credentials and submits -> user managment table
    # TODO (3) after submitting for, app generates an encryption key and unique ID
    # TODO (4) display uniqiue ID and use either block/stream cipher to encrypt the file (credential(s)) and thus generate ciphertext
    # TODO (5) generate has values of the ciphertext and unique ID
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
    # TODO (7) performs file checksum and IF TRUE/
    # TODO provides the file/record for viewing/downloading/
    # TODO else file/record is corrupt and cannot be displayed/downloaded

def main():
    app_menu() # start menu

    # TODO needed SQL "on premise" user access management table
    
if __name__ == '__main__':
    main()
