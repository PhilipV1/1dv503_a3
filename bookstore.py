from getpass import getpass
from mysql.connector import connect, Error
from enum import Enum


class Menu(Enum):
    """Easier readability for menu options"""
    MAIN = 0
    USER = 1
    NEWMEMBER = 2
    QUIT = 3


class UserMenu(Enum):
    """Easier readability for menu options"""
    BROWSE = 1
    SEARCH = 2
    CHECKOUT = 3
    LOGOUT = 4


class BrowseOptions(Enum):
    """Easier readability for menu options"""
    ERROR = -1
    RETURN = 0
    ADDTOCART = 1
    CONTINUE = 2


def main():
    run = True
    userin = Menu.MAIN.value
    sqlConnector = connectDB()
    if sqlConnector != 0:
        while run:
            if userin == Menu.MAIN.value:
                menuType(Menu.MAIN.value)
                userin = userInput(Menu.MAIN.value)
            if userin == Menu.USER.value:
                menuType(Menu.USER.value)
                userin = userInput(Menu.USER.value)
                if userin == UserMenu.BROWSE.value:
                    browseSubject(sqlConnector)
                    userin = Menu.USER.value
                if userin == UserMenu.LOGOUT.value:
                    userin = Menu.MAIN.value
            if userin == Menu.NEWMEMBER.value:
                newMemberMenu(sqlConnector)
                input("\nPress enter to return to the main menu")
                userin = Menu.MAIN.value
            if userin == Menu.QUIT.value:
                run = False

        sqlConnector.close()


def connectDB():

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
        return 0
    return connection


def browseSubject(sqlConnector):
    """Lets the user select a subject and display the books in that subject"""
    searchQuery = """SELECT DISTINCT subject FROM books ORDER BY subject"""
    with sqlConnector.cursor() as cursor:
        cursor.execute(searchQuery)
        result = cursor.fetchall()
        print()
        for count, row in enumerate(result):
            print(f"{count + 1}. {row[0]}")
        # Get the selected genre
        selection = selectSubject(len(result))
        subject = result[selection - 1][0]
        amountQuery = f"""SELECT count(*) FROM books
            WHERE subject = \"{subject}\""""
        cursor.execute(amountQuery)
        nrOfBooks = cursor.fetchall()

        subjectQuery = f"""SELECT author, title, isbn, price, subject
        FROM books WHERE subject = \"{subject}\"
        ORDER BY author LIMIT 0, 2"""
        print(f"\"{subject}\"")
        cursor.execute(subjectQuery)
        books = cursor.fetchall()
        print(f"{nrOfBooks[0][0]} available books on this subject\n")
        for b in books:
            print(f"Author: {b[0]}")
            print(f"Title: {b[1]}")
            print(f"ISBN: {b[2]}")
            print(f"Price: {b[3]}")
            print(f"Subject: {b[4]}\n")

        # Continue as long as user does not return to main menu
        returnMain = False
        # Offset keeps track of which books to show
        offset = 2
        while not returnMain:
            prompt = """Enter ISBN to add to cart or enter \"n\" to browse
                or ENTER to return to menu:\n"""
            userin = input(prompt)
            option = browseSelection(userin)
            if option == BrowseOptions.ERROR.value:
                print("\nPlease input a valid option!\n")
            if option == BrowseOptions.RETURN.value:
                returnMain = True
            if option == BrowseOptions.CONTINUE.value:
                # Query for the 2 current books to show
                subjectQuery = f"""SELECT author, title, isbn, price, subject
                    FROM books WHERE subject = \"{subject}\"
                    ORDER BY author LIMIT {offset}, 2"""
                offset = (offset + 2) % nrOfBooks[0][0]
                cursor.execute(subjectQuery)
                books = cursor.fetchall()
                for b in books:
                    print(f"Author: {b[0]}")
                    print(f"Title: {b[1]}")
                    print(f"ISBN: {b[2]}")
                    print(f"Price: {b[3]}")
                    print(f"Subject: {b[4]}\n")
            if option == BrowseOptions.ADDTOCART.value:
                bookExistQuery = f"""SELECT * FROM books
                    WHERE isbn = {userin}"""
                cursor.execute(bookExistQuery)
                book = cursor.fetchall()
                if len(book) == 0:
                    print("Invalid ISBN, book not found")
                else:
                    pass


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
        memberMenuOption()


def memberMenuOption():
    print("\t1. Browse by Subject")
    print("\t2. Search by Author/Title")
    print("\t3. Check out")
    print("\t4. Logout")


def mainMenuOption():
    print("\t1. Member login")
    print("\t2. New Member Registration")
    print("\t3. Quit\n")


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


# REMOVE LATER
def printMembers(sqlConnector):
    selectMembers = "SELECT * FROM members"
    with sqlConnector.cursor() as cursor:
        cursor.execute(selectMembers)
        result = cursor.fetchall()
        for index, row in enumerate(result):
            print(f"{index}. {row[0]}")


# Section for input related functions
def userInput(currentMenu):
    if currentMenu == Menu.MAIN.value:
        validInputs = [1, 2, 3]
    elif currentMenu == Menu.USER.value:
        validInputs = [1, 2, 3, 4]

    option = False
    while not option:
        try:
            value = int(input("\nType in your option: "))
            if validInputs.count(value) < 1:
                print("Please choose from the appropriate options")
            else:
                option = True
        except ValueError as e:
            print(f"Invalid input: {e}")
    return value


def selectSubject(count):
    validInputs = [i for i in range(1, count + 1)]
    option = False
    while not option:
        try:
            selection = int(input("Enter your choice: "))
            if validInputs.count(selection) > 0:
                option = True
            else:
                print("Please input a valid choice.\n")
        except ValueError as e:
            print("Invalid input! ERROR: " + e)

    return selection


def browseSelection(userinput):
    retVal = -1

    if userinput == "":
        retVal = BrowseOptions.RETURN.value
    elif userinput.isnumeric():
        retVal = BrowseOptions.ADDTOCART.value
    elif userinput.lower() == "n":
        retVal = BrowseOptions.CONTINUE.value
    else:
        retVal = BrowseOptions.ERROR.value

    return retVal


if __name__ == "__main__":
    main()
