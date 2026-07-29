class Fooditem:
    def __init__(self, item_id, name, price, available, cost_price):
        self.item_id = item_id
        self.name = name
        self.price = price
        self._available = available
        self.__cost_price = cost_price
        self.total_items = 0
    def get_cost_price(self):
        if self.__cost_price <= 0:
            raise ValueError("Cost price must be greater than 0.")
        return self.__cost_price
    def get_price(self):
        if self.price <= 0:
            raise ValueError("Price must be greater than 0.")
        return self.price
    def set_cost_price(self, cost_price):
        if cost_price <= 0:
            raise ValueError("Cost price must be greater than 0.")
        self.__cost_price = cost_price
        return self.__cost_price
    def change_price(self, new_price):
        if new_price <= 0:
            raise ValueError("Price must be greater than 0.")
        self.price = new_price
        return self.price
    def display(self):
        print(f"Item ID: {self.item_id}")
        print(f"Name: {self.name}")
        print(f"Price: {self.price}")
        print(f"Available: {self._available}")
        print(f"Cost Price: {self.__cost_price}")

    @staticmethod
    def calculate_tax(self, price):
        tax_rate = 0.1  # 10% tax rate
        return price * tax_rate
  
    def get_total_items(cls):
      return cls.total_items

class Pizza(Fooditem):
    def __init__(self, item_id, name, price, available, cost_price, size):
        super().__init__(item_id, name, price, available, cost_price)
        self.size = size
        self.total_items += 1

    def display(self):
        super().display()
        print(f"Size: {self.size}")
class Discountable:
    def __init__(self, discount_percentage):
        self.discount_percentage = discount_percentage
    def apply_discount(self, discount_percentage):
        if discount_percentage < 0 or discount_percentage > 100:
            raise ValueError("Discount percentage must be between 0 and 100.")
        discount_amount = self.price * (discount_percentage / 100)
        self.price -= discount_amount
        return self.price
    