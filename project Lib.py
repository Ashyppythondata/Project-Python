import sqlite3
from datetime import datetime

# Fixed Admin Username and Password
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Database Connection
db = sqlite3.connect("library_updated.db")
cursor = db.cursor()

# Create Members Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS members (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

# Create Books Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT,
    author TEXT,
    status TEXT DEFAULT 'Available',
    borrower TEXT,
    borrow_date TEXT,
    return_date TEXT
)
""")

# Create Deleted Books Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS deleted_books (
    id INTEGER,
    title TEXT,
    author TEXT,
    deleted_date TEXT
)
""")

# Create Borrowing History Table
cursor.execute("""
CREATE TABLE IF NOT EXISTS history (
    book_id INTEGER,
    title TEXT,
    member TEXT,
    borrow_date TEXT,
    return_date TEXT
)
""")

db.commit()


# Check Date
def check_date(date):
    try:
        datetime.strptime(date, "%d-%m-%Y")
        return True
    except ValueError:
        print("Invalid date! Use DD-MM-YYYY")
        return False


# Member Registration
def register():
    print("\n--- Member Registration ---")

    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()

    if username == "" or password == "":
        print("Username and password cannot be empty!")
        return

    try:
        cursor.execute(
            "INSERT INTO members VALUES (?, ?)",
            (username, password)
        )
        db.commit()
        print("Member registered successfully!")

    except sqlite3.IntegrityError:
        print("Username already exists!")


# Admin Login
def admin_login():
    print("\n--- Admin Login ---")

    username = input("Enter admin username: ")
    password = input("Enter admin password: ")

    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        print("Admin login successful!")
        admin_menu()
    else:
        print("Invalid admin username or password!")


# Member Login
def member_login():
    print("\n--- Member Login ---")

    username = input("Enter username: ")
    password = input("Enter password: ")

    cursor.execute(
        "SELECT * FROM members WHERE username=? AND password=?",
        (username, password)
    )

    if cursor.fetchone():
        print("Member login successful!")
        print("Welcome", username)
        member_menu(username)
    else:
        print("Invalid username or password!")


# Add Books
def add_book():
    while True:
        print("\n--- Add Book ---")

        title = input("Enter book title: ").strip()
        author = input("Enter author name: ").strip()

        if title == "" or author == "":
            print("Title and author cannot be empty!")
        else:
            cursor.execute(
                "INSERT INTO books (title, author) VALUES (?, ?)",
                (title, author)
            )
            db.commit()
            print("Book added successfully!")

        choice = input("Do you want to add another book? (yes/no): ")

        if choice.lower() != "yes":
            break


# View Books
def view_books():
    print("\n--- Book List ---")

    cursor.execute(
        "SELECT id, title, author, status FROM books"
    )
    books = cursor.fetchall()

    print("ID | Title | Author | Status")
    print("---------------------------------------------")

    if not books:
        print("No books available!")

    for book in books:
        print(*book, sep=" | ")


# Update Book
def update_book():
    print("\n--- Update Book ---")

    view_books()

    book_id = input("Enter book ID: ")
    title = input("Enter new title: ").strip()
    author = input("Enter new author: ").strip()

    if title == "" or author == "":
        print("Title and author cannot be empty!")
        return

    cursor.execute(
        "UPDATE books SET title=?, author=? WHERE id=?",
        (title, author, book_id)
    )
    db.commit()

    if cursor.rowcount > 0:
        print("Book updated successfully!")
    else:
        print("Book not found!")


# Delete Book
def delete_book():
    print("\n--- Delete Book ---")

    view_books()
    book_id = input("Enter book ID to delete: ")

    cursor.execute(
        "SELECT id, title, author FROM books WHERE id=? AND status='Available'",
        (book_id,)
    )

    book = cursor.fetchone()

    if book:
        date = datetime.now().strftime("%d-%m-%Y")

        cursor.execute(
            "INSERT INTO deleted_books VALUES (?, ?, ?, ?)",
            (book[0], book[1], book[2], date)
        )

        cursor.execute(
            "DELETE FROM books WHERE id=?",
            (book_id,)
        )

        db.commit()
        print("Book deleted successfully!")
    else:
        print("Book not found or currently borrowed!")


# View Deleted Books
def view_deleted():
    print("\n--- Deleted Books ---")

    cursor.execute("SELECT * FROM deleted_books")
    books = cursor.fetchall()

    print("ID | Title | Author | Deleted Date")
    print("---------------------------------------------")

    if not books:
        print("No deleted books!")

    for book in books:
        print(*book, sep=" | ")


# Borrow Book - Member
def borrow_book(username):
    print("\n--- Borrow Book ---")

    view_books()

    book_id = input("Enter book ID: ")
    title = input("Enter book title: ").strip()
    borrow_date = input("Enter borrowing date (DD-MM-YYYY): ")

    if not check_date(borrow_date):
        return

    cursor.execute(
        """UPDATE books
           SET status='Borrowed',
               borrower=?,
               borrow_date=?,
               return_date=NULL
           WHERE id=? AND title=? AND status='Available'""",
        (username, borrow_date, book_id, title)
    )

    if cursor.rowcount > 0:
        db.commit()
        print("Book borrowed successfully!")
        print("Borrowing Date:", borrow_date)
    else:
        print("Book not available or incorrect ID/title!")


# Return Book - Admin and Member
def return_book(username, role):
    print("\n--- Return Book ---")

    book_id = input("Enter book ID: ")
    title = input("Enter book title: ").strip()
    return_date = input("Enter return date (DD-MM-YYYY): ")

    if not check_date(return_date):
        return

    if role == "Admin":
        cursor.execute(
            """SELECT id, title, borrower, borrow_date
               FROM books
               WHERE id=? AND title=? AND status='Borrowed'""",
            (book_id, title)
        )
    else:
        cursor.execute(
            """SELECT id, title, borrower, borrow_date
               FROM books
               WHERE id=? AND title=? AND borrower=?
               AND status='Borrowed'""",
            (book_id, title, username)
        )

    book = cursor.fetchone()

    if book:
        borrow_date = datetime.strptime(book[3], "%d-%m-%Y")
        returned = datetime.strptime(return_date, "%d-%m-%Y")

        if returned < borrow_date:
            print("Return date cannot be before borrowing date!")
            return

        cursor.execute(
            """INSERT INTO history
               VALUES (?, ?, ?, ?, ?)""",
            (book[0], book[1], book[2], book[3], return_date)
        )

        cursor.execute(
            """UPDATE books
               SET status='Available',
                   borrower=NULL,
                   borrow_date=NULL,
                   return_date=?
               WHERE id=?""",
            (return_date, book_id)
        )

        db.commit()
        print("Book returned successfully!")
        print("Return Date:", return_date)
    else:
        print("Invalid book ID/title or return not allowed!")


# View Borrowed Books - Admin
def view_borrowed():
    print("\n--- Currently Borrowed Books ---")

    cursor.execute(
        """SELECT id, title, borrower, borrow_date
           FROM books WHERE status='Borrowed'"""
    )

    books = cursor.fetchall()

    print("ID | Title | Member | Borrow Date")
    print("------------------------------------------------")

    if not books:
        print("No borrowed books!")

    for book in books:
        print(*book, sep=" | ")


# View Borrowing History - Admin
def view_history():
    print("\n--- Borrowing History ---")

    cursor.execute("SELECT * FROM history")
    records = cursor.fetchall()

    print("ID | Title | Member | Borrow Date | Return Date")
    print("-------------------------------------------------------")

    if not records:
        print("No borrowing history!")

    for record in records:
        print(*record, sep=" | ")


# Admin Menu
def admin_menu():
    while True:
        print("\n===== ADMIN MENU =====")
        print("1. Add Book")
        print("2. View Books")
        print("3. Update Book")
        print("4. Delete Book")
        print("5. View Borrowed Books")
        print("6. Return Book")
        print("7. View Deleted Books")
        print("8. View Borrowing History")
        print("9. Logout")

        choice = input("Enter choice: ")

        if choice == "1":
            add_book()
        elif choice == "2":
            view_books()
        elif choice == "3":
            update_book()
        elif choice == "4":
            delete_book()
        elif choice == "5":
            view_borrowed()
        elif choice == "6":
            return_book("", "Admin")
        elif choice == "7":
            view_deleted()
        elif choice == "8":
            view_history()
        elif choice == "9":
            print("Admin logged out!")
            break
        else:
            print("Invalid choice!")


# Member Menu
def member_menu(username):
    while True:
        print("\n===== MEMBER MENU =====")
        print("1. View Books")
        print("2. Borrow Book")
        print("3. Return Book")
        print("4. Logout")

        choice = input("Enter choice: ")

        if choice == "1":
            view_books()
        elif choice == "2":
            borrow_book(username)
        elif choice == "3":
            return_book(username, "Member")
        elif choice == "4":
            print("Member logged out!")
            break
        else:
            print("Invalid choice!")


# Main Menu
def main():
    while True:
        print("\n===== LIBRARY MANAGEMENT SYSTEM =====")
        print("1. Admin Login")
        print("2. Member Registration")
        print("3. Member Login")
        print("4. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            admin_login()
        elif choice == "2":
            register()
        elif choice == "3":
            member_login()
        elif choice == "4":
            print("Thank you!")
            break
        else:
            print("Invalid choice!")


main() #run program
db.close()  #exit program
