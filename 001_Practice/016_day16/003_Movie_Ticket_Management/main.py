#13. Movie Ticket Management
class Movie:
    def __init__(self, movie_id, movie_name, theater, ticket_price, is_available=True):
        self.movie_id = movie_id
        self.movie_name = movie_name
        self.theater = theater
        self.ticket_price = ticket_price
        self.is_available = is_available

    def display_movie_info(self):
        print(f"Movie ID: {self.movie_id}")
        print(f"Movie Name: {self.movie_name}")
        print(f"Theater: {self.theater}")
        print(f"Ticket Price: ${self.ticket_price}")
        print(f"Available: {'Yes' if self.is_available else 'No'}")

    def update_ticket_price(self, new_price):
        self.ticket_price = new_price
        print(f"Ticket price updated to ${self.ticket_price}")

class TicketManagement(Movie):
    def __init__(self, movie_id, movie_name, theater, ticket_price, is_available=True):
        super().__init__(movie_id, movie_name, theater, ticket_price, is_available)

    def book_ticket(self):
        if self.is_available:
            self.is_available = False
            print(f"Ticket for '{self.movie_name}' booked successfully.")
        else:
            print(f"Sorry, tickets for '{self.movie_name}' are not available.")

    def cancel_ticket(self):
        if not self.is_available:
            self.is_available = True
            print(f"Ticket for '{self.movie_name}' canceled successfully.")
        else:
            print(f"No booking found for '{self.movie_name}' to cancel.")
movie1 = TicketManagement(1, "Inception", "Cinema Hall 1", 12.5)
movie1.display_movie_info()
movie1.book_ticket()
movie1.display_movie_info()
movie1.cancel_ticket()
movie1.display_movie_info()