#10. Airline Ticket Management
class Ticket:
  def __init__(self, ticket_id, passenger_name, destination, ticket_price):
    self.ticket_id = ticket_id
    self.passenger_name = passenger_name  
    self.destination = destination
    self.ticket_price = ticket_price
    self.is_booked = False

  def display_ticket_info(self):
    print(f"Ticket ID: {self.ticket_id}")
    print(f"Passenger Name: {self.passenger_name}")
    print(f"Destination: {self.destination}")
    print(f"Ticket Price: ${self.ticket_price}")
    print(f"Is Booked: {self.is_booked}")

  def update_ticket_price(self, new_price):
    self.ticket_price = new_price

class TicketManagement(Ticket): 
   def __init__(self, ticket_id, passenger_name, destination, ticket_price):
        super().__init__(ticket_id, passenger_name, destination, ticket_price)
        self.tickets = []

   def book_ticket(self, ticket):
    if not ticket.is_booked:
      ticket.is_booked = True
      self.tickets.append(ticket)
      print("Ticket booked successfully.")
    else:
      print("Ticket is already booked.")

   def cancel_ticket(self, ticket):
    if ticket.is_booked:
      ticket.is_booked = False
      self.tickets.remove(ticket)
      print("Ticket canceled successfully.")
    else:
      print("Ticket is not booked.")

ticketmanagement1 = TicketManagement(1, "John Doe", "New York", 300)
ticketmanagement1.display_ticket_info()
ticketmanagement1.update_ticket_price(350)
ticketmanagement1.display_ticket_info()
ticketmanagement1.book_ticket(ticketmanagement1)
ticketmanagement1.display_ticket_info()
ticketmanagement1.cancel_ticket(ticketmanagement1)
ticketmanagement1.display_ticket_info()