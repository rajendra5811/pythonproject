#4. Hotel Room Management System
class Room:
    def __init__(self, room_id, room_type, price_per_day, floor, is_available=True):
        self.room_id = room_id
        self.room_type = room_type
        self.price_per_day = price_per_day
        self.floor = floor
        self.is_available = is_available
    def display_room_info(self):
        availability = "Available" if self.is_available else "Not Available"
        print(f"Room ID: {self.room_id}")
        print(f"Room Type: {self.room_type}")
        print(f"Price per Day: ${self.price_per_day}")
        print(f"Floor: {self.floor}")
        print(f"Availability: {availability}")
    def update_room_price(self, new_price):
      self.price_per_day = new_price
        print(f"Room price updated to ${self.price_per_day}")

class RoomManagement(Room):
    def __init__(self, room_id, room_type, price_per_day, floor, is_available=True):
        super().__init__(room_id, room_type, price_per_day, floor, is_available)

    def book_room(self, days):
        if self.is_available:
            total_cost = self.price_per_day * days
            self.is_available = False
            print(f"Room {self.room_id} booked for {days} days. Total cost: ${total_cost}")
        else:
            print(f"Room {self.room_id} is not available for booking.")

    def display_room_info(self):
        super().display_room_info()
    def update_room_price(self, new_price):
        super().update_room_price(new_price)
    def checkout_room(self):
        if not self.is_available:
            self.is_available = True
            print(f"Room {self.room_id} checked out.")
        else:
            print(f"Room {self.room_id} is already available. No checkout needed.")

room1 = RoomManagement(room_id=101, room_type="Deluxe", price_per_day=150, floor=1)
room1.display_room_info()
room1.update_room_price(200)
room1.display_room_info()
room1.book_room(3)
room1.book_room(2)
room1.checkout_room()
room1.book_room(1)
