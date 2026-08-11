5. Gym Membership Management
class Member:
    def __init__(self, member_id, name, membership_type, monthly_fee):
        self.member_id = member_id
        self.name = name
        self.membership_type = membership_type
        self.monthly_fee = monthly_fee
        self.is_active = False

    def display_member_info(self):
        print(f"Member ID: {self.member_id}")
        print(f"Name: {self.name}")
        print(f"Membership Type: {self.membership_type}")
        print(f"Monthly Fee: ${self.monthly_fee}")
        print(f"Status: {'Active' if self.is_active else 'Inactive'}")

    def update_membership(self, new_type):
        self.membership_type = new_type

class MembershipManagement(Member):
    def __init__(self, member_id, name, membership_type, monthly_fee):
        super().__init__(member_id, name, membership_type, monthly_fee)


    def display_member_info(self):                       
        super().display_member_info()

    def update_membership(self, new_type):
        super().update_membership(new_type) 

def activate_membership(self):  
    if not self.is_active:
        self.is_active = True
        print(f"Membership for {self.name} has been activated.")
    else:
        print(f"Membership for {self.name} is already active.")

def deactivate_membership(self):
    if self.is_active:
        self.is_active = False
        print(f"Membership for {self.name} has been deactivated.")
    else:
        print(f"Membership for {self.name} is already inactive.")

gym1=MembershipManagement(1, "John Doe", "Premium", 50)
gym1.display_member_info()
gym1.activate_membership()
gym1.display_member_info()
gym1.update_membership("Standard")
gym1.display_member_info()
gym1.deactivate_membership()
gym1.display_member_info()