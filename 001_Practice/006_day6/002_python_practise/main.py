class Vehicle:
    def __init__(self, vehicle_number, owner_name, vehicle_type):
        self.vehicle_number = vehicle_number
        self.owner_name = owner_name
        self.vehicle_type = vehicle_type

    def display(self):
        print(f"{self.vehicle_number}\t{self.owner_name}\t{self.vehicle_type}")


class ParkingSlot:
    def __init__(self, slot_number, hourly_rate):
        self.slot_number = slot_number
        self.hourly_rate = hourly_rate
        self.vehicle = None
        self.is_available = True

    def park_vehicle(self, vehicle):
        self.vehicle = vehicle
        self.is_available = False

    def remove_vehicle(self):
        self.vehicle = None
        self.is_available = True

    def display(self):
        status = "Available" if self.is_available else "Occupied"
        print(f"{self.slot_number}\t{status}\tRate: {self.hourly_rate}")


class ParkingTicket:
    def __init__(self, ticket_id, vehicle, slot, hours):
        self.ticket_id = ticket_id
        self.vehicle = vehicle
        self.slot = slot
        self.hours = hours
        self.total_amount = hours * slot.hourly_rate

    def display(self):
        print(
            f"{self.ticket_id}\t"
            f"{self.vehicle.vehicle_number}\t"
            f"{self.slot.slot_number}\t"
            f"{self.hours}\t"
            f"{self.total_amount}"
        )


class ParkingLot:
    def __init__(self):
        self.slots = []
        self.tickets = []

    # -------------------
    # ADD TEMPLATE
    # -------------------
    def add_slot(self, slot):
        self.slots.append(slot)
        print("Slot Added Successfully")

    # -------------------
    # SEARCH TEMPLATE
    # -------------------
    def find_slot(self, slot_number):
        for slot in self.slots:
            if slot.slot_number == slot_number:
                return slot
        return None

    def find_ticket(self, ticket_id):
        for ticket in self.tickets:
            if ticket.ticket_id == ticket_id:
                return ticket
        return None

    def find_vehicle(self, vehicle_number):
        for slot in self.slots:
            if slot.vehicle and slot.vehicle.vehicle_number == vehicle_number:
                return slot.vehicle
        return None

    # -------------------
    # DISPLAY TEMPLATE
    # -------------------
    def display_slots(self):
        print("\nSlot\tStatus\tRate")
        print("-" * 30)

        for slot in self.slots:
            slot.display()

    def display_tickets(self):
        print("\nTicket\tVehicle\tSlot\tHours\tAmount")
        print("-" * 50)

        for ticket in self.tickets:
            ticket.display()

    # -------------------
    # FILTER TEMPLATE
    # -------------------
    def available_slots(self):
        available = []

        for slot in self.slots:
            if slot.is_available:
                available.append(slot)

        return available

    # -------------------
    # COORDINATION TEMPLATE
    # -------------------
    def park_vehicle(self, ticket_id, vehicle, slot_number, hours):

        slot = self.find_slot(slot_number)

        if slot is None:
            print("Slot Not Found")
            return

        if not slot.is_available:
            print("Slot Already Occupied")
            return

        slot.park_vehicle(vehicle)

        ticket = ParkingTicket(ticket_id, vehicle, slot, hours)

        self.tickets.append(ticket)

        print("Vehicle Parked Successfully")
        print("Bill =", ticket.total_amount)

    def remove_vehicle(self, ticket_id):

        ticket = self.find_ticket(ticket_id)

        if ticket is None:
            print("Ticket Not Found")
            return

        ticket.slot.remove_vehicle()

        self.tickets.remove(ticket)

        print("Vehicle Removed Successfully")

    # -------------------
    # STATE CHANGE / CALCULATION
    # -------------------
    def calculate_bill(self, ticket_id):

        ticket = self.find_ticket(ticket_id)

        if ticket:
            print("Total Bill =", ticket.total_amount)
        else:
            print("Ticket Not Found")


# -----------------------------
# Main Program
# -----------------------------

lot = ParkingLot()

lot.add_slot(ParkingSlot(1, 50))
lot.add_slot(ParkingSlot(2, 50))
lot.add_slot(ParkingSlot(3, 100))

car1 = Vehicle("AP39AB1234", "Raj", "Car")
bike1 = Vehicle("AP39XY5678", "Rahul", "Bike")

lot.park_vehicle(101, car1, 1, 3)
lot.park_vehicle(102, bike1, 2, 2)

lot.display_slots()

print("\nAvailable Slots")
for slot in lot.available_slots():
    print(slot.slot_number)

lot.display_tickets()

lot.calculate_bill(101)

lot.remove_vehicle(101)

lot.display_slots()

