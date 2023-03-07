from getpass import getpass
from mysql.connector import connect, Error

def main():
    run = True
    userin = '0'
    sqlConnector = ConnectDB()
    
    while run:
        if userin == '0':
            MenuType(0)
            userin = UserInput()
        if userin == '1':
            MenuType(1)
            userin = '0'
        if userin == "2":
            NewMemberMenu(sqlConnector)
            PrintMembers(sqlConnector)
            input("Press enter to return to the main menu")
            userin = '0'
        if userin.lower() == 'q':
            run = False
        else:
            userin = '0'

def ConnectDB():
    try:
        account = input("Enter username: ")
        pword = getpass("Enter password: ")
        with connect(
            host = "localhost",
            user = account,
            password = pword,
            database = "book_store",
        ) as connection:
            print(connection)
    except Error as e:
        print("Error generated message: " + e)
    return connection

def MenuType(menuType=0):
    line1 = "*******************************************\n"
    line2 = "***                                     ***\n"
    line3 = "***   Welcome to the Online Bookstore   ***\n"
    if menuType == 0:
        print(line1 + line2+ line3+ line2+ line1)
        MainMenuOption()
    if menuType == 1:
        line4 = "***            Member Menu              ***\n"
        print(line1 + line2 + line3 + line4 + line2 + line1)
        
    
def MainMenuOption():
    print("\t1. Member login")
    print("\t2. New Member Registration")
    print("\tQ. Quit\n")

def NewMemberMenu(sqlConnector):
    print(sqlConnector)
    print("New member registration\n")

    fname = input("Enter first name: ")
    lname = input("Enter last name: ")
    staddress = input("Enter street address: ")
    city = input("Enter city: ")
    state = input("Enter state: ")
    try:
        zipCode = int(input("Enter zip: "))
    except:
        print("Please enter a valid zip code")
    phone = input("Enter phone number: ")
    email = input("Enter email address: ")
    userID = input("Enter userID: ")
    password = input("Enter password: ")

    valueString = "(" + fname + ", " + lname + ", " + staddress + ", " + city + ", " + state + ", " + str(zipCode) + ", " + phone + ", " + email + ", " + password + ")"
    insertMember = """INSERT INTO members (fname, lname, address, city, state, zip, phone, email, password)
    VALUES """ + valueString
    
    with sqlConnector.cursor() as cursor:
        cursor.execute(insertMember)
        sqlConnector.commit()


    print("You have registered successfully")


def PrintMembers(sqlConnector):
    selectMembers = "SELECT * FROM members"
    with sqlConnector.cursor() as cursor:
        cursor.execute(selectMembers)
        result = cursor.fetchall()
        for row in result:
            print(row)

def UserInput():
    try:
        option = False
        while not option:
            value = str(input("Type in your option: "))
            if value != '1' and value != '2' and value != 'q' and value != 'Q':
                print("Please choose from the appropriate options")
            else:
                option = True
    except:
        print("Please enter a valid input")
    return value



if __name__ == "__main__":
    main()