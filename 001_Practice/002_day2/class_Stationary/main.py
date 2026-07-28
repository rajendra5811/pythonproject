# porject: Stationary Store Management System
# new thing :  self.customer = Customer() vs = []
class person:
    def __init__(self, person_id, name, phone):
        self.person_id = person_id                                                
        self.name = name
        self.phone = phone

    def greet(self):
        return f"Hello, my name is {self.name} and my phone number is {self.phone}."

class Customer(person):
    def __init__(self, person_id, name, phone, customer_id):
        super().__init__(person_id, name, phone)
        self.customer_id = customer_id
        self.reward_points = 0
        self.shopping_cart = ShoppingCart()

class Employee(person):
    def __init__(self, person_id, name, phone, employee_id):
        super().__init__(person_id, name, phone)
        self.employee_id = employee_id
        self.salary = 0
        self.department = None     

class Product:
    def __init__(self, product_id, name, price, stock):
        self.product_id = product_id
        self.name = name
        self.__cost_price = 0
        self._stock = stock

    def get_cost_price(self):
        return self.__cost_price

    def set_cost_price(self, cost_price):
        if cost_price < 0:
            raise ValueError("Cost price cannot be negative.")
        self.__cost_price = cost_price

class Notebook(Product):                      
    def __init__(self, product_id, name, price, stock, pages):
        super().__init__(product_id, name, price, stock)
        self.pages = pages
class PremiumNotebook(Notebook):
    def __init__(self, product_id, name, price, stock, pages, cover_material):
        super().__init__(product_id, name, price, stock, pages)
        self.cover_material = cover_material
class Pen(Product):
    def __init__(self, product_id, name, price, stock, color):
        super().__init__(product_id, name, price, stock)
        self.ink_color =  str(input("Enter the ink color of the pen: ")).lower()

class Marker(Product):
    def __init__(self, product_id, name, price, stock, marker_type):
        super().__init__(product_id, name, price, stock)
        self.marker_type = str(input("Enter the type of the marker (e.g., permanent, whiteboard): ")).lower()

class Supplier(person):
    def __init__(self, person_id, name, phone, supplier_id , company_name):
        super().__init__(person_id, name, phone)
        self.supplier_id = supplier_id
        self.company_name = company_name
        self.products_supplied = []

class ShoppingCart:
    def __init__(self):
        self.cart_items = []

class Order:
    def __init__(self, order_id, customer, products, total_amount, status):
        self.order_id = int(input("Enter the order ID: "))  
        self.customer = Customer()
        self.products = []
        self.total_amount = total_amount
        self.status = status
class StationaryStore:
    def __init__(self, store_id, products, customers, employees, suppliers, orders):
        self.store_id = int(input("Enter the store ID: "))
        self.products = []
        self.customers = []
        self.employees = []
        self.suppliers = []
        self.orders = []

