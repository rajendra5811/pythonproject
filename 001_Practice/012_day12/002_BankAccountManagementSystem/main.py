#2. Bank Account Management System
class BankAccount:
    def __init__(self, account_number, customer_name, balance, account_type):
        self.account_number = account_number
        self.customer_name = customer_name
        self.balance = balance
        self.account_type = account_type

    def display_account_info(self):
        print(f"Account Number: {self.account_number}")
        print(f"Customer Name: {self.customer_name}")
        print(f"Balance: {self.balance}")
        print(f"Account Type: {self.account_type}")

    def update_account_type(self, new_type):
        self.account_type = new_type
        print(f"Account type updated to: {self.account_type}")

    def deposit(self, amount):
        self.balance += amount
        print(f"Amount deposited. New balance: {self.balance}")

    def withdraw(self, amount):
        if self.balance >= amount:
            self.balance -= amount
            print(f"Amount withdrawn. New balance: {self.balance}")
        else:
            print("Insufficient balance.")

class AccountManagement(BankAccount):
    def __init__(self, account_number, customer_name, balance, account_type):
        super().__init__(account_number, customer_name, balance, account_type)


    def display_account_info(self):
        super().display_account_info()
        print(f"Account Type: {self.account_type}")
    
    def update_account_type(self, new_type):
        super().update_account_type(new_type)

    def deposit(self, amount):
        super().deposit(amount)

    def withdraw(self, amount):
        super().withdraw(amount)
account = AccountManagement(1001, "Raj", 5000, "Savings")
account.withdraw(2000)
account.deposit(15000)
account.display_account_info()
account.update_account_type("Current")
account.withdraw(100000)
account.display_account_info()



