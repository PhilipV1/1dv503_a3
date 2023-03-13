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
    ISBNERROR = -2
    ERROR = -1
    RETURN = 0
    ADDTOCART = 1
    CONTINUE = 2


def main():
    run = True
    loggedin = False
    userin = Menu.MAIN.value
    currentUser = createEmptyDict()
    sqlConnector = connectDB()

    if sqlConnector != 0:
        while run:
            if userin == Menu.MAIN.value:
                menuType(Menu.MAIN.value)
                userin = userInput(Menu.MAIN.value)
            if userin == Menu.USER.value:
                if not loggedin:
                    loggedin = login(sqlConnector, currentUser)
                    userin = Menu.USER.value
                else:
                    menuType(Menu.USER.value)
                    userin = userInput(Menu.USER.value)
                    if userin == UserMenu.BROWSE.value:
                        browseSubject(sqlConnector, currentUser)
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
    """Connects to the database, returns 0 on failure"""
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


def createEmptyDict():
    userDict = {
        "fname": "none",
        "lname": "none",
        "address": "none",
        "city": "none",
        "state": "none",
        "zip": 0,
        "phone": 0,
        "email": "none",
        "userid": 0
    }
    return userDict


def login(sqlConnector, currentUser):
    with sqlConnector.cursor() as cursor:
        validInput = False
        while not validInput:
            email = input("Enter your email: ")
            password = getpass("Enter your password: ")
            userQuery = f"""SELECT fname, lname, address, city, state, zip,
            phone, email, userid, password
            FROM members WHERE email = \"{email}\" AND password = \"{password}\""""
            cursor.execute(userQuery)
            user = cursor.fetchone()
            if user is None or len(user) == 0:
                print("""Wrong credentials,
                        please enter correct username/password\n""")
                check = input("""Press ENTER to continue or type \"exit\"
                        to return to main menu: """)
                if check.lower() == "exit":
                    return False
            else:
                currentUser.update({"fname": user[0]})
                currentUser.update({"lname": user[1]})
                currentUser.update({"address": user[2]})
                currentUser.update({"city": user[3]})
                currentUser.update({"state": user[4]})
                currentUser.update({"zip": user[5]})
                currentUser.update({"phone": user[6]})
                currentUser.update({"email": user[7]})
                currentUser.update({"userid": user[8]})
                validInput = True
    return True


def browseSubject(sqlConnector, currentUser):
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
                or press ENTER to return to menu:\n"""
            userin = input(prompt)
            option = browseSelection(userin)
            if option == BrowseOptions.ERROR.value:
                print("\nPlease input a valid option!\n")
            if option == BrowseOptions.ISBNERROR.value:
                print("ERROR: ISBN Length > 10\n")
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
                # Check if the book exist in the books table
                bookExistQuery = f"""SELECT 1 FROM books
                    WHERE isbn = {userin}"""
                cursor.execute(bookExistQuery)
                book = cursor.fetchone()
                if book is None:
                    print(f"\nBook not found! ISBN: {userin}\n")
                else:
                    addToCart(sqlConnector, userin, currentUser)
                    checkCart(cursor, currentUser.get("userid"))


def addToCart(sqlConnector, isbn, currentUser):
    """Inserts a book into the cart table in the database"""
    userid = currentUser.get("userid")
    with sqlConnector.cursor() as cursor:
        validInput = False
        while not validInput:
            try:
                qty = int(input("Enter quantity: "))
                validInput = True
            except ValueError as ve:
                print("Error!: " + ve)

        if qty == 0:
            # Check if the book already exists in the cart to remove it
            checkCart = f"""SELECT 1 FROM cart WHERE isbn = {isbn}
            AND userid = {userid}"""
            cursor.execute(checkCart)
            exist = cursor.fetchone()
            if exist is not None:
                removeFromCart = f"""DELETE from cart WHERE isbn = {isbn}
                AND userid = {userid}"""
                cursor.execute(removeFromCart)
                cursor.commit()
                print(f"ISBN: {isbn} removed from cart!\n")
        elif qty > 0:
            # Add qty number of books of the given isbn to the cart
            checkIfExist = f"""SELECT 1 FROM cart WHERE userid = {userid}
            AND isbn = {isbn}"""
            cursor.execute(checkIfExist)
            exists = cursor.fetchone()
            if exists is None:
                addBook = f"""INSERT INTO cart
                (userid, isbn, qty)
                VALUES ({userid}, {isbn}, {qty})"""
                cursor.execute(addBook)
                sqlConnector.commit()
                print(f"Book added to cart! ISBN: {isbn}, Quantity: {qty}\n")
            else:
                updateCart = f"""UPDATE cart SET qty = {qty}
                WHERE isbn = {isbn} AND userid = {userid}"""
                cursor.execute(updateCart)
                sqlConnector.commit()
                print(f"Cart updated! ISBN: {isbn}, Quantity: {qty}")
        else:
            print("Please enter a valid quantity!\n")


def checkCart(cursor, userid):
    check = f"""SELECT * FROM cart WHERE userid = {userid}"""
    cursor.execute(check)
    cart = cursor.fetchall()
    print("Books in cart: \n")
    for row in cart:
        print(row)


def menuType(menu=Menu.MAIN.value):
    line1 = "*******************************************\n"
    line2 = "***                                     ***\n"
    line3 = "***   Welcome to the Online Bookstore   ***\n"
    if menu == Menu.MAIN.value:
        print(line1 + line2 + line3 + line2 + line1)
        print("\t1. Member login")
        print("\t2. New Member Registration")
        print("\t3. Quit\n")
    if menu == Menu.USER.value:
        line4 = "***            Member Menu              ***\n"
        print(line1 + line2 + line3 + line4 + line2 + line1)
        print("\t1. Browse by Subject")
        print("\t2. Search by Author/Title")
        print("\t3. Check out")
        print("\t4. Logout")


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
        if len(userinput) > 10:
            retVal = BrowseOptions.ISBNERROR.value
        else:
            retVal = BrowseOptions.ADDTOCART.value
    elif userinput.lower() == "n":
        retVal = BrowseOptions.CONTINUE.value
    else:
        retVal = BrowseOptions.ERROR.value

    return retVal


if __name__ == "__main__":
    main()
