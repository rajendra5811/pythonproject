class Car:
    def __init__(self, car_id, brand, model, rental_price_per_day):
        self.car_id = car_id
        self.brand = brand
        self.model = model
        self.rental_price_per_day= rental_price_per_day
        self.is_available=True

    def display_car_info(self):
        print(f"Car ID : {self.car_id}")
        print(f"Brand : {self.brand}")
        print(f"Model : {self.model}")
        print(f"Rental Price per Day : ${self.rental_price_per_day}")
        print(f"Is Available : {self.is_available}")

    def update_rental_price(self, new_price):
        self.rental_price_per_day = new_price
        print(f"Rental Price updated successfully, New price is : {self.rental_price_per_day}$ per day!!")

class RentalManagement(Car):

    def __init__(self, car_id, brand, model, rental_price_per_day ):
        super().__init__(car_id, brand, model, rental_price_per_day)
       
    def rent_car(self, days):
        if self.is_available:
            self.is_available = False
            print("Car rented successfully.")
            print(f"Days Rented : {days}")
            print(f"Price Per Day : {self.rental_price_per_day}")
            print(f"Total Cost : $ {self.rental_price_per_day * days}")
        else:
            print("Sorry! This car is currently unavailable.")

    def return_car(self):
        print("Car returned successfully.")
        self.is_available = True
        print("The car is now available for rent.")

    

car1 = RentalManagement(car_id=101, brand="Toyota", model="Camry", rental_price_per_day = 70)

car1.display_car_info()
car1.update_rental_price(85)
car1.display_car_info()
car1.rent_car(5)
car1.rent_car(10)
car1.return_car()
car1.rent_car(2)