class Car:
    def __init__(self,car_id, brand, model, rental_price_per_day):
        self.car_id = car_id
        self.brand = brand
        self.model = model
        self.rental_price_per_day = rental_price_per_day
        self.is_available = is_available

    def display_car_info(self):
        print(f"car_id:{self.car_id}\t brand:{self.brand}\t model:{self.model}\t rental_price:{self.rental_price_per_day}\t is_available:{self.is_available}")
    def update_rental_price(self, new_price):
        if new_price >0:
           self.rental_price_per_day = new_price
           return True
        return self.rental_price_per_day
        
class RentalManagement(Car):
    def  __init__(self,car_id, brand, model, rental_price_per_day, is_available):
        super().__init__(car_id, brand, model, rental_price_per_day, is_available)
        
    def rent_car(self, days):
        if days >0 or self.is_available == True:
            print(f"rental_price:{self.rental_price_per_day}\t days:{days}")
            print(f"car{self.car_id} is rented successfully")
            return self.car_id
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


