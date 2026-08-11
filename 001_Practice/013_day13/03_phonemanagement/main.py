#6. Mobile Phone Management System
class MobilePhone:
    def __init__(self, phone_id, brand, model, price, is_available):
        self.phone_id = phone_id
        self.brand = brand
        self.model = model
        self.price = price
        self.is_available = is_available

    def display_phone_info(self):
        print(f"Phone ID: {self.phone_id}")
        print(f"Brand: {self.brand}")
        print(f"Model: {self.model}")
        print(f"Price: ${self.price}")
        print(f"Available: {self.is_available}")

    def update_price(self, new_price):
        self.price = new_price


class PhoneManagement(MobilePhone):
    def __init__(self, phone_id, brand, model, price, is_available):
        super().__init__(phone_id, brand, model, price, is_available)

  
    def purchase_phone(self):
        if self.is_available:
            self.is_available = False
            print(f"Phone {self.phone_id} purchased successfully.")
        else:
            print(f"Phone {self.phone_id} is not available for purchase.")

    def return_phone(self):
        if not self.is_available:
            self.is_available = True
            print(f"Phone {self.phone_id} returned successfully.")
        else:
            print(f"Phone {self.phone_id} was not purchased and cannot be returned.")
phone1 = PhoneManagement(1, "Apple", "iPhone 13", 999, True)
phone2 = PhoneManagement(2, "Samsung", "Galaxy S21", 799, True)
phone1.display_phone_info() 
phone1.purchase_phone()
phone1.display_phone_info()
phone1.return_phone()
phone1.display_phone_info()
phone1.update_price(899)
phone1.display_phone_info()

