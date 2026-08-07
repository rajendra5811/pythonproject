# ===========================================
# Class 1: Room (Parent Class)
# ===========================================
class Room:
    def __init__(self, room_number, room_type, price_per_night, is_booked=False):
        self.room_number = room_number
        self.room_type = room_type
        self.price_per_night = price_per_night
        self.is_booked = is_booked

    def display_room_info(self):
        status = "Yes" if self.is_booked else "No"
        print(f"Room Number: {self.room_number}")
        print(f"Room Type: {self.room_type}")
        print(f"Price per Night: ${self.price_per_night}")
        print(f"Booked: {status}\n")

    def update_room_price(self, new_price):
        self.price_per_night = new_price
        print("Room price updated successfully.")
        print(f"New Price per Night: ${self.price_per_night}\n")


# ===========================================
# Class 2: RoomBooking (Child Class)
# ===========================================
class RoomBooking(Room):
    def book_room(self, nights):
        if self.is_booked:
            print("Sorry! This room is currently booked.\n")
        else:
            total_cost = self.price_per_night * nights
            self.is_booked = True
            print("Room booked successfully.\n")
            print(f"Nights Stayed: {nights}")
            print(f"Price Per Night: ${self.price_per_night}")
            print(f"Total Cost: ${total_cost}\n")

    def checkout_room(self):
        self.is_booked = False
        print("Checked out successfully.")
        print("The room is now available for new guests.\n")


# ===========================================
# Driver Code
# ===========================================
if __name__ == "__main__":
    # 1. Create one object with sample values
    booking = RoomBooking(302, "Deluxe Suite", 150)

    # 2. Display the room information
    print("--- Initial Room Info ---")
    booking.display_room_info()

    # 3. Update the room price to $180
    print("--- Updating Room Price ---")
    booking.update_room_price(180)

    # 4. Display the updated information
    print("--- Updated Room Info ---")
    booking.display_room_info()

    # 5. Book the room for 4 nights
    print("--- Booking Room (4 Nights) ---")
    booking.book_room(4)

    # 6. Try booking the same room again without checking out
    print("--- Attempting Double Booking ---")
    booking.book_room(3)

    # 7. Check out of the room
    print("--- Checking Out ---")
    booking.checkout_room()

    # 8. Book the room again for 2 nights
    print("--- Booking Room (2 Nights) ---")
    booking.book_room(2)