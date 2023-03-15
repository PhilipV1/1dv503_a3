from getpass import getpass
from mysql.connector import connect, Error
from enum import Enum
from datetime import datetime, timedelta


class Menu(Enum):
    """Easier readability for menu options"""
    MAIN = 0
    USER = 1
    NEWMEMBER = 2
    QUIT = 3
    BROWSE = 4
    SEARCH = 5
    CHECKOUT = 6
    LOGOUT = 7


class Options(Enum):
    """Easier readability for menu options"""
    ISBNERROR = -2
    ERROR = -1
    ADDTOCART = 1
    CONTINUE = 2
    RETURN = 3
    AUTHORSEARCH = 4
    TITLESEARCH = 5


def main():
    run = True
    loggedin = False
    menu = Menu.MAIN.value
    currentUser = createEmptyDict()
    sqlConnector = connectDB()

    if sqlConnector != 0:
        while run:
            if menu == Menu.MAIN.value:
                menuType(Menu.MAIN.value)
                menu = menuInput(Menu.MAIN.value)
            if menu == Menu.USER.value:
                if not loggedin:
                    loggedin = login(sqlConnector, currentUser)
                    menu = Menu.USER.value
                else:
                    menuType(Menu.USER.value)
                    menu = menuInput(Menu.USER.value)
                    if menu == Menu.BROWSE.value:
                        browseSubject(sqlConnector, currentUser)
                        menu = Menu.USER.value
                    if menu == Menu.SEARCH.value:
                        searchAuthorTitle(sqlConnector, currentUser)
                        menu = Menu.USER.value
                    if menu == Menu.CHECKOUT.value:
                        checkout(sqlConnector, currentUser)
                        menu = Menu.USER.value
                    if menu == Menu.LOGOUT.value:
                        menu = Menu.MAIN.value
            if menu == Menu.NEWMEMBER.value:
                newMemberMenu(sqlConnector)
                input("\nPress enter to return to the main menu")
                menu = Menu.MAIN.value
            if menu == Menu.QUIT.value:
                run = False

        sqlConnector.close()


def connectDB():
    """Connects to the database, returns 0 on failure"""
    try:
        # account = input("Enter username: ")
        # pword = getpass("Enter password: ")
        account = "root"
        pword = "EpcEsp343!"
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
            # email = input("Enter your email: ")
            # password = getpass("Enter your password: ")
            email = 'philipvelandria@gmail.com'
            password = '12345'
            userQuery = f"""SELECT fname, lname, address, city, state, zip,
            phone, email, userid, password
            FROM members WHERE email = \"{email}\"
            AND password = \"{password}\""""
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
    userid = currentUser.get("userid")
    # Get the selected genre
    result = getSubjects(sqlConnector)
    selected = selectSubject(len(result))
    subject = result[selected - 1][0]
    offset = 0  # Offset keeps track of which books to show

    # Display the first two books found
    condition = "subject"
    nrOfBooks = getBookAmountSpecific(sqlConnector, condition, subject)
    print(f"{nrOfBooks} available books in this subject!")
    subjectQuery(sqlConnector, offset, subject, nrOfBooks)
    offset = (offset + 2) % nrOfBooks

    # Continue as long as the user doesn't return to main menu
    option = 0
    while option != Options.RETURN.value:
        userin = getInput()
        menu = Menu.BROWSE.value

        option = selection(userin, menu)
        if option == Options.ERROR.value:
            print("\nPlease input a valid option!\n")
        if option == Options.ISBNERROR.value:
            print("ERROR: ISBN Length > 10\n")
        if option == Options.CONTINUE.value:
            # Query for the 2 current books to show
            subjectQuery(sqlConnector, offset, subject, nrOfBooks)
            offset = (offset + 2) % nrOfBooks
        if option == Options.ADDTOCART.value:
            # Check if the book exist in the books table
            if not checkBookExist(sqlConnector, userin):
                print(f"\nBook not found! ISBN: {userin}\n")
            else:
                addToCart(sqlConnector, userin, userid)
                checkCart(sqlConnector, userid)


def getSubjects(sqlConnector):
    with sqlConnector.cursor() as cursor:
        getSubjectQuery = """SELECT DISTINCT subject FROM books
                            ORDER BY subject"""
        cursor.execute(getSubjectQuery)
        result = cursor.fetchall()
        print()
        for count, row in enumerate(result):
            print(f"{count + 1}. {row[0]}")
    return result


def searchAuthorTitle(sqlConnector, currentUser):
    """Search and display books based on author or title search"""
    userid = currentUser.get("userid")
    option = 0

    while option != Options.RETURN.value:
        searchMenu()
        userin = input("\nType in your choice: ")
        option = selection(userin, Menu.SEARCH.value)
        if option == Options.AUTHORSEARCH.value:
            authorBrowse(sqlConnector, userid)
        elif option == Options.TITLESEARCH.value:
            titleBrowse(sqlConnector, userid)
        else:
            option = Options.RETURN.value


def titleBrowse(sqlConnector, userid):
    option = 0
    offset = 0
    condition = "title"
    orderBy = condition
    title = input("Enter title or part of a title: ")
    nrOfBooks = getBookAmount(sqlConnector, condition, title)
    nrOfBooks = nrOfBooks[0]  # Turning the tuple into the int value
    print(f"{nrOfBooks} book(s) found!")
    # Display the first set of books if there are any
    if nrOfBooks > 0:
        searchQuery(sqlConnector, offset, title, nrOfBooks, condition,
                    orderBy)
        offset = (offset + 3) % nrOfBooks
    # Allows the user to browse through the books or add them to cart
    while option != Options.RETURN.value:
        userin = getInput()
        option = selection(userin, Menu.BROWSE.value)
        if option == Options.CONTINUE.value:
            searchQuery(sqlConnector, offset, title, nrOfBooks, condition,
                        orderBy)
        elif option == Options.ADDTOCART.value:
            addToCart(sqlConnector, userin, userid)


def authorBrowse(sqlConnector, userid):
    option = 0
    condition = "author"
    orderBy = condition
    offset = 0  # Which rows will be selected from the database
    author = input("Enter author name: ")
    nrOfBooks = getBookAmount(sqlConnector, condition, author)
    nrOfBooks = nrOfBooks[0]  # Turning the tuple into the int value
    print(f"{nrOfBooks} book(s) found!\n")
    # Displays the first number of books if there are any
    if nrOfBooks > 0:
        searchQuery(sqlConnector, offset, author, nrOfBooks, condition,
                    orderBy)
        offset = (offset + 3) % nrOfBooks

    while option != Options.RETURN.value:
        userin = getInput()
        option = selection(userin, Menu.BROWSE.value)

        if option == Options.CONTINUE.value:
            searchQuery(sqlConnector, offset, author, nrOfBooks, condition,
                        orderBy)
        elif option == Options.ADDTOCART.value:
            addToCart(sqlConnector, userin, userid)


def getBookAmountSpecific(sqlConnector, condition, search):
    """Query used when condition has to exactly match the search"""
    with sqlConnector.cursor() as cursor:
        amountQuery = f"""SELECT count(*) FROM books
                        WHERE {condition} = \"{search}\""""
        cursor.execute(amountQuery)
        nrOfBooks = cursor.fetchone()

    return nrOfBooks[0]


def getBookAmount(sqlConnector, condition, search):
    """Query used when condition has to partially match the search"""
    with sqlConnector.cursor() as cursor:
        amountQuery = f"""SELECT count(*) FROM books
                        WHERE {condition} LIKE \"%{search}%\""""
        cursor.execute(amountQuery)
        nrOfBooks = cursor.fetchone()

    return nrOfBooks


def checkBookExist(sqlConnector, isbn):
    with sqlConnector.cursor() as cursor:
        bookExistQuery = f"""SELECT 1 FROM books
                            WHERE isbn = {isbn}"""
        cursor.execute(bookExistQuery)
        result = cursor.fetchone()
        if result is None or result[0] < 1:
            return False
        else:
            return True


def subjectQuery(sqlConnector, offset, subject, nrOfBooks):
    """Query for browsing specific subjects"""
    with sqlConnector.cursor() as cursor:
        subjectQuery = f"""SELECT author, title, isbn, price, subject
        FROM books WHERE subject = \"{subject}\"
        ORDER BY author LIMIT {offset}, 2"""
        cursor.execute(subjectQuery)
        books = cursor.fetchall()
        for b in books:
            print(f"Author: {b[0]}")
            print(f"Title: {b[1]}")
            print(f"ISBN: {b[2]}")
            print(f"Price: {b[3]}")
            print(f"Subject: {b[4]}\n")


def searchQuery(sqlConnector, offset, search, nrOfBooks, condition, orderBy):
    """Customizable SQL query depending on condition, search string,
    order by, offset and maximum items to display"""
    with sqlConnector.cursor() as cursor:
        authorQuery = f"""SELECT author, title, isbn, price, subject
                        FROM books WHERE {condition} LIKE \"%{search}%\"
                        ORDER BY {orderBy} LIMIT {offset}, 3"""
        cursor.execute(authorQuery)
        result = cursor.fetchall()
        offset = (offset + 3) % nrOfBooks

        for book in result:
            print(f"Author: {book[0]}")
            print(f"Title: {book[1]}")
            print(f"ISBN: {book[2]}")
            print(f"Price: {book[3]}")
            print(f"Subject: {book[4]}\n")


def addToCart(sqlConnector, isbn, userid):
    """Inserts a book into the cart table in the database"""
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
            if checkExistInCart(sqlConnector, isbn, userid):
                removeFromCart = f"""DELETE from cart WHERE isbn = {isbn}
                AND userid = {userid}"""
                cursor.execute(removeFromCart)
                sqlConnector.commit()
                print(f"ISBN: {isbn} removed from cart!\n")
        elif qty > 0:
            # Add qty number of books of the given isbn to the cart
            if not checkExistInCart(sqlConnector, isbn, userid):
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


def checkCart(sqlConnector, userid):
    with sqlConnector.cursor() as cursor:
        check = f"""SELECT * FROM cart WHERE userid = {userid}"""
        cursor.execute(check)
        cart = cursor.fetchall()
        print("Books in cart: \n")
        for row in cart:
            print(row)


def checkExistInCart(sqlConnector, isbn, userid):
    with sqlConnector.cursor() as cursor:
        bookExistQuery = f"""SELECT 1 FROM cart
                        WHERE isbn = {isbn} AND userid = {userid}"""
        cursor.execute(bookExistQuery)
        result = cursor.fetchone()
        if result is None or result[0] < 1:
            return False
        else:
            return True


def checkout(sqlConnector, currentUser):
    userid = currentUser.get("userid")
    print(userid)
    displayCart(sqlConnector, userid)
    deliveryDate = datetime.date(datetime.today()) + timedelta(weeks=1)
    print(f"Estimated delivery date: {deliveryDate}")


def getCartISBN(sqlConnector, userid):
    """Collects ISBN, Title, Price and Quantity for all books in the cart.
    Returns a 2 dimensional array"""
    with sqlConnector.cursor() as cursor:
        searchQuery = f"""SELECT isbn, qty FROM cart WHERE userid = {userid}"""
        cursor.execute(searchQuery)
        result = cursor.fetchall()
        isbnArray = [0 for i in range(len(result))]
        data = [[0 for i in range(4)] * len(result)]
        for index, row in enumerate(result):
            print(row[0])
            isbnArray[index] = row[0]
            getBookPriceTitle(sqlConnector, isbnArray[index])
    return isbnArray


def getBookPriceTitle(sqlConnector, isbn):
    query = f"""SELECT title, price FROM books WHERE isbn = {isbn}"""
    with sqlConnector.cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
        for row in result:
            print(row)


def getCart(sqlConnector, userid):
    isbnArray = getCartISBN(sqlConnector, userid)
    fields = 4
    cartData = [[0 for i in range(fields)] * len(isbnArray)]


def displayCart(sqlConnector, userid):
    descriptors = [['ISBN', 'Title', 'Price $', 'Total']]
    isbnWidth = 10
    titleWidth = 30
    priceWidth = 8
    totalWidth = 8
    pad = 3
    # Used for formatting the cart in columns
    separator = '-' * (isbnWidth + titleWidth + priceWidth + totalWidth + pad)
    firstFormat = f'{{:<{isbnWidth}}} {{:<{titleWidth}}}'
    secondFormat = f'{{:>{priceWidth}}} {{:>{totalWidth}}}'
    formatting = firstFormat + secondFormat
    getCart(sqlConnector, userid)
    for i in range(len(descriptors)):
        if i == 0:
            print(formatting.format(descriptors[i][0], descriptors[i][1],
                                    descriptors[i][2], descriptors[i][3]))
            print(separator)
    # Take input
    print("Proceed to checkout  (Y/N)?: ")


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


def searchMenu():
    print("1. Author search")
    print("2. Title search")
    print("3. Return to main menu")


# Section for input related functions
def menuInput(currentMenu):
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
                # The addition is to avoid using multiple enum classes since
                # the UI shows either 1-3 or 1-4 when the menu class has 1-7
                # this converts the user menu options of 1-4 to 4-7
                if currentMenu == Menu.USER.value:
                    value += 3
                option = True
        except ValueError as e:
            print(f"Invalid input: {e}")
    return value


def getInput():
    """Asks the user for an input for ISBN, browse or return to main menu"""
    prompt = """Enter ISBN to add to cart or enter \"n\" to browse
                or press ENTER to return to menu:\n"""
    userin = input(prompt)

    return userin


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


def selection(userinput, menuType):
    """Selection function when the user searches/browse books"""
    retVal = -1
    # Selection for browse by subject
    if menuType == Menu.BROWSE.value:
        if userinput == "":
            retVal = Options.RETURN.value
        elif userinput.isnumeric():
            if len(userinput) > 10:
                retVal = Options.ISBNERROR.value
            else:
                retVal = Options.ADDTOCART.value
        elif userinput.lower() == "n":
            retVal = Options.CONTINUE.value
        else:
            retVal = Options.ERROR.value
    # Selection for Author/Title search
    if menuType == Menu.SEARCH.value:
        if userinput == "1":
            retVal = Options.AUTHORSEARCH.value
        elif userinput == "2":
            retVal = Options.TITLESEARCH.value
        elif userinput == "3":
            retVal = Options.RETURN.value
        else:
            retVal = Options.ERROR.value

    return retVal


if __name__ == "__main__":
    main()
