class Car:
    def __init__(self, car_id, brand, model, rental_price_per_day, is_available=True):
        self.car_id = car_id
        self.brand = brand
        self.model = model
        self.rental_price_per_day = rental_price_per_day
        self.is_available = is_available


    def display_car_info(self):
        availability = "Yes" if self.is_available else "No"
        print(f"Car ID: {self.car_id}")
        print(f"Brand: {self.brand}")
        print(f"Model: {self.model}")
        print(f"Rental Price per Day: ${self.rental_price_per_day}")
        print(f"Available: {availability}")


    def  update_rental_price(self, new_price):
        if new_price > 0:
            self.rental_price_per_day = new_price
        return self.rental_price_per_day
    
class RentalManagement(Car):
    def __init__(self, car_id, brand, model, rental_price_per_day, is_available=True):
         super().__init__(car_id, brand, model, rental_price_per_day, is_available)

    def rent_car(self, days):
        if self.is_available:
            total_cost = self.rental_price_per_day * days
            self.is_available = False
            print("Car rented successfully.")
            print()
            print(f"Days Rented: {days}")
            print(f"Price Per Day: ${self.rental_price_per_day}")
            print(f"Total Cost: ${total_cost}")
            print()
            self.display_car_info()
            return total_cost
        else:
            print("Sorry! This car is currently unavailable.")
            return False
     

    def return_car(self):
       self.is_available = True
       print("Car returned successfully.")
       print("The car is now available for rent.")
   
rental = RentalManagement(101, "Toyota", "Camry", 70)
rental.display_car_info()
print()
rental.update_rental_price(85)
rental.display_car_info()
print()
rental.rent_car(5)
print()
rental.rent_car(5)
print()
rental.return_car()
print()
rental.rent_car(2)

