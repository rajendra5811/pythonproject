#9. Parking Slot Management
class ParkingSlot:
   def __init__(self, slot_id, vehicle_number, slot_type, price_per_hour):
         self.slot_id = slot_id
         self.vehicle_number = vehicle_number
         self.slot_type = slot_type
         self.price_per_hour = price_per_hour
         self.is_available = True

   def display_slot_info(self):
        print(f"SlotID:{self.slot_id}")
        print(f"Vehicle Number:{self.vehicle_number}")
        print(f"Slot Type:{self.slot_type}")    

   def update_price(self, new_price):
        self.price_per_hour = new_price
        return f"Price updated to: {self.price_per_hour}"

class ParkingManagement(ParkingSlot):
     def __init__(self, slot_id, vehicle_number, slot_type, price_per_hour):
         super().__init__(slot_id, vehicle_number, slot_type, price_per_hour)

     def park_vehicle(self, hours):
          if self.is_available == True:
              self.is_available = False
              total_cost = hours * self.price_per_hour
              return f"Vehicle parked. Total cost: {total_cost}"
     def remove_vehicle(self):
          if self.is_available == False:
              self.is_available = True
              return "Vehicle removed. Slot is now available."
          return "No vehicle to remove."

parkingManagement = ParkingManagement("A1", "KA-01-AB-1234", "Compact", 20)
parkingManagement.display_slot_info()
parkingManagement.update_price(25)
parkingManagement.park_vehicle(3)
parkingManagement.remove_vehicle()
parkingManagement.display_slot_info()