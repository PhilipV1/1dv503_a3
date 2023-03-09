from getpass import getpass
from mysql.connector import connect, Error
from enum import Enum


class Menu(Enum):
    """Easier readability for menu options"""
    MAIN = 0
    USER = 1
    NEWMEMBER = 2
    QUIT = 3


def main():
    run = True
    userin = Menu.MAIN
    sqlConnector = ConnectDB()

    while run:
        if userin == Menu.MAIN.value:
            menuType(Menu.MAIN.value)
            userin = userInput()
        if userin == Menu.USER.value:
            menuType(Menu.USER.value)
            userin = Menu.MAIN.value
        if userin == Menu.NEWMEMBER.value:
            newMemberMenu(sqlConnector)
            input("\nPress enter to return to the main menu")
            userin = Menu.MAIN.value
        if userin == Menu.QUIT.value:
            run = False
        else:
            userin = Menu.MAIN.value

    sqlConnector.close()


def ConnectDB():

    try:
        account = input("Enter username: ")
        pword = getpass("Enter password: ")
        connection = connect(
            host="localhost",
            user=account,
            password=pword,
            database="book_store",
        )
    except Error as e:
        print("Failed to connect to database: " + e.msg)
    return connection


def menuType(menu=Menu.MAIN.value):
    line1 = "*******************************************\n"
    line2 = "***                                     ***\n"
    line3 = "***   Welcome to the Online Bookstore   ***\n"
    if menu == Menu.MAIN.value:
        print(line1 + line2 + line3 + line2 + line1)
        mainMenuOption()
    if menu == Menu.USER.value:
        line4 = "***            Member Menu              ***\n"
        print(line1 + line2 + line3 + line4 + line2 + line1)


def memberMenuOption():
    print("\t1. Browse by Subject")
    print("\t2. Search by Author/Title")
    print("\t3. Check out")
    print("\t4. Logout")


def mainMenuOption():
    print("\t1. Member login")
    print("\t2. New Member Registration")
    print("\t3. Show all members")
    print("\tQ. Quit\n")


def newMemberMenu(sqlConnector):
    """Inserts a new member into the database using SQL queries"""
    print(sqlConnector)
    print("New member registration\n")

    fname = input("Enter first name: ")
    lname = input("Enter last name: ")
    staddress = input("Enter street address: ")
    city = input("Enter city: ")
    state = input("Enter state: ")
    try:
        zipCode = int(input("Enter zip: "))
    except ValueError as e:
        print(f"Not a valid zip code ERROR: {e}")
    phone = input("Enter phone number: ")
    email = input("Enter email address: ")
    password = input("Enter password: ")

    valueString = f"""
    INSERT INTO members
    (fname, lname, address, city, state, zip, phone, email, password)
    VALUES
    ("{fname}", "{lname}", "{staddress}", "{city}", "{state}",
    {zipCode}, "{phone}", "{email}", "{password}")
    """
    # Handle error if the user tries to enter a duplicate user
    try:
        with sqlConnector.cursor() as cursor:
            cursor.execute(valueString)
            sqlConnector.commit()
            print("You have registered successfully")
    except Error as e:
        print(f"Failed to created new member: {e.msg}\n")


def printMembers(sqlConnector):
    selectMembers = "SELECT * FROM members"
    with sqlConnector.cursor() as cursor:
        cursor.execute(selectMembers)
        result = cursor.fetchall()
        for row in result:
            print(row)


def userInput():
    validInputs = [1, 2, 3]

    option = False
    while not option:
        try:
            value = int(input("Type in your option: ")).lower()
            ordValue = ord(value)
            print(f"ASCII value = {ordValue}")
            if validInputs.count(validInputs) < 1:
                print("Please choose from the appropriate options")
            else:
                option = True
        except ValueError as e:
            print(f"Invalid input: {e}")
    return value


if __name__ == "__main__":
    main()
