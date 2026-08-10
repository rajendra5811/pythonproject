#1. Library Book Management System
class Book: 
    def __init__(self, book_id, title, author, price, is_available=True):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.price = price
        self.is_available = is_available
    def display_book_info(self):
        print(f"Book ID: {self.book_id}")
        print(f"Title: {self.title}")
        print(f"Author: {self.author}")
        print(f"Price: ${self.price}")
        print(f"Available: {'Yes' if self.is_available else 'No'}")
    def update_price(self, new_price):
        self.price = new_price
        return f"Price updated to ${self.price}"

class LibraryManagement(Book):
    def __init__(self,book_id, title, author, price, is_available=True):
        super().__init__(book_id, title, author, price, is_available)
        self.books = []
    def borrow_book(self, days):
        if self.is_available:
            borrowing_fee = self.price * days * 0.1  # Assuming 10% of price per day
            self.is_available = False
            print(f"Book borrowed for {days} days. Borrowing fee: ${borrowing_fee:.2f}")
        else:
            print("Sorry, the book is currently unavailable.")
    def return_book(self):
        if not self.is_available:
            self.is_available = True
            print("Book returned successfully.")
        else:
            print("This book is already available.")

library_book = LibraryManagement(201, "Python Programming", "Raj Kumar", 50)
library_book.display_book_info()
library_book.borrow_book(5)
library_book.display_book_info()
library_book.return_book()
library_book.update_price(60)
library_book.display_book_info()





