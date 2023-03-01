def main():
    run = True
    userin = 0
    while run:
        if userin == 0:
            MenuSign("Welcome to the Online Book Store")
        userin = UserInput()
        if userin == '1':
            MenuSign("Welcome to the Online Book Store\n\tMember Menu")
        if userin.lower() == 'q':
            run = False

def MenuSign(sign, menuType = ""):
    welcomeSign = sign
    padding = 12
    width = len(welcomeSign) + padding
    height = 6
    star = "*"
    space = " "
    for h in range(height):
        for w in range(width):
            if h == 0 or h == (height - 1):
                print(star, end="")
            elif (h == ((height // 2) - 1) and w >= (0 + padding // 2) and w < width - (padding // 2)):
                print(welcomeSign[w - (padding // 2)], end="")
            #elif (h == (height // 2) and w >= (width // 2) - ):
            elif (w < 3 or w >= width - 3 and h != 0 and h != height - 1):
                print(star, end="")
            else:
                print(" ", end="")
        print()
    MainMenuOption()
    
def MainMenuOption():
    print("\t1. Member login")
    print("\t2. New Member Registration")
    print("\tQ. Quit")

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