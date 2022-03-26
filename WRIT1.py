
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
            print("add")
        elif selection == '2':
            print("view")
        elif selection == '3':
            break
        else:
            print("Unkown Option!")
            

def main():
    app_menu() # start menu

    # TODO needed SQL "on premise" user access management table
    # TODO appropriate 
    
if __name__ == '__main__':
    main()
