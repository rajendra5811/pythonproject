#8.Employee Leave management System
class Employee:
    def __init__(self, employee_id, name, department):
        self.employee_id = employee_id
        self.name = name
        self.department = department
        self.available_leave = 0
        self.is_on_leave = False
    def display_employee_info(self):
            print(f"Employee ID: {self.employee_id}")
            print(f"Name: {self.name}")
            print(f"Department: {self.department}")
            print(f"Available Leave: {self.available_leave}")
            print(f"Is on Leave: {self.is_on_leave}")
    
    
    def update_department(self, new_department):
            self.department = new_department
            print(f"Department updated to: {self.department}")

class LeaveManagement(Employee):
    def __init__(self, employee_id, name, department):
        super().__init__(employee_id, name, department)

    def apply_leave(self, days):
         if self.is_on_leave == False and self.available_leave >= days:
              self.available_leave -= days
              self.is_on_leave = True
              return f"Leave applied for {days} days. Remaining leave: {self.available_leave}"
         elif self.is_on_leave == True:
              return "Cannot apply for leave. Employee is already on leave."

    def return_to_work(self):
            if self.is_on_leave == True:
                self.is_on_leave = False
                return "Employee has returned to work."
            else:
                return "Employee is not on leave."

leave_management = LeaveManagement("E001", "John Doe", "HR")
leave_management.available_leave = 10
leave_management.display_employee_info()
leave_management.update_department("Finance")
leave_management.apply_leave(5)
leave_management.return_to_work()
leave_management.display_employee_info()