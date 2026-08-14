#7. Vehicle Service Management
class Vehicle:
    def __init__(self, vehicle_id, brand, model, service_cost):
        self.vehicle_id = vehicle_id
        self.brand = brand
        self.model = model
        self.service_cost = service_cost
        self.is_serviced = False

    def display_vehicle_info(self):
        print(f"Vehicle ID: {self.vehicle_id}")
        print(f"Brand: {self.brand}")
        print(f"Model: {self.model}")
        print(f"Service Cost: {self.service_cost}")
        print(f"Is Serviced: {self.is_serviced}")

    def update_service_cost(self, new_cost):
        self.service_cost = new_cost
class ServiceManagement(Vehicle):
    def __init__(self, vehicle_id, brand, model, service_cost):
        super().__init__(vehicle_id, brand, model, service_cost)
        self.is_serviced = False

    def send_for_service(self):
        if self.is_serviced == False:
            print(f"Vehicle {self.vehicle_id} sent for service.")
            self.is_serviced = True

    def complete_service(self):
        if self.is_serviced == True:
            print(f"Vehicle {self.vehicle_id} service completed.")
            self.is_serviced = False
service_management = ServiceManagement("V001", "Toyota", "Camry", 200)
service_management.display_vehicle_info()
service_management.send_for_service()
service_management.complete_service()
service_management.update_service_cost(250)
service_management.display_vehicle_info()
