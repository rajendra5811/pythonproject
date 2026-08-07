from abc import ABC, abstractmethod


class Vehicle(ABC):
    """Common parent class for all vehicles."""

    total_vehicles = 0

    def __init__(self, vehicle_id: str, brand: str, model: str, rental_price_per_day: float, is_available: bool = True):
        if not self.validate_vehicle_id(vehicle_id):
            raise ValueError("Vehicle ID must follow format VEH-1001")

        self.vehicle_id = vehicle_id
        self.brand = brand
        self.model = model
        self._rental_price_per_day = None
        self._is_available = is_available

        self.rental_price_per_day = rental_price_per_day

        Vehicle.total_vehicles += 1

    @staticmethod
    def validate_vehicle_id(vehicle_id: str) -> bool:
        """Validate vehicle ID format like VEH-1001."""
        if not isinstance(vehicle_id, str):
            return False
        parts = vehicle_id.split("-")
        return len(parts) == 2 and parts[0] == "VEH" and parts[1].isdigit()

    @property
    def rental_price_per_day(self) -> float:
        return self._rental_price_per_day

    @rental_price_per_day.setter
    def rental_price_per_day(self, value: float):
        if value <= 0:
            raise ValueError("rental_price_per_day must be greater than zero")
        self._rental_price_per_day = float(value)

    @property
    def is_available(self) -> bool:
        return self._is_available

    def display_details(self):
        print(
            f"Vehicle ID: {self.vehicle_id}\n"
            f"Brand: {self.brand}\n"
            f"Model: {self.model}\n"
            f"Rental Price/Day: {self.rental_price_per_day}\n"
            f"Available: {self.is_available}"
        )

    def rent_vehicle(self):
        if not self._is_available:
            raise ValueError(f"Vehicle {self.vehicle_id} is already rented")
        self._is_available = False

    def return_vehicle(self):
        if self._is_available:
            raise ValueError(f"Vehicle {self.vehicle_id} is already available")
        self._is_available = True

    def calculate_rental_cost(self, number_of_days: int) -> float:
        if number_of_days <= 0:
            raise ValueError("number_of_days must be greater than zero")
        return self.rental_price_per_day * number_of_days

    @classmethod
    def get_total_vehicle_count(cls) -> int:
        return cls.total_vehicles

    def __str__(self):
        return f"{self.__class__.__name__}({self.vehicle_id}, {self.brand}, {self.model})"


class Car(Vehicle):
    """Car class inheriting from Vehicle."""

    def __init__(
        self,
        vehicle_id: str,
        brand: str,
        model: str,
        rental_price_per_day: float,
        number_of_seats: int,
        fuel_type: str,
        has_air_conditioning: bool,
        is_available: bool = True,
    ):
        super().__init__(vehicle_id, brand, model, rental_price_per_day, is_available)

        if number_of_seats <= 0:
            raise ValueError("number_of_seats must be greater than zero")

        self.number_of_seats = number_of_seats
        self.fuel_type = fuel_type
        self.has_air_conditioning = has_air_conditioning

    def calculate_rental_cost(self, number_of_days: int) -> float:
        base_cost = super().calculate_rental_cost(number_of_days)
        return base_cost * 1.10

    def calculate_long_trip_discount(self, number_of_days: int) -> float:
        final_cost = self.calculate_rental_cost(number_of_days)
        if number_of_days >= 7:
            return final_cost * 0.85
        return final_cost

    def check_family_suitability(self, required_seats: int) -> bool:
        return self.number_of_seats >= required_seats

    def display_details(self):
        super().display_details()
        print(
            f"Seats: {self.number_of_seats}\n"
            f"Fuel Type: {self.fuel_type}\n"
            f"Air Conditioning: {self.has_air_conditioning}"
        )

    def __str__(self):
        return f"Car({self.vehicle_id}, {self.brand}, {self.model}, seats={self.number_of_seats})"


class Bike(Vehicle):
    """Bike class inheriting from Vehicle."""

    allowed_types = {"Sports", "Cruiser", "Scooter", "Electric"}

    def __init__(
        self,
        vehicle_id: str,
        brand: str,
        model: str,
        rental_price_per_day: float,
        engine_capacity: int,
        helmet_included: bool,
        bike_type: str,
        is_available: bool = True,
    ):
        super().__init__(vehicle_id, brand, model, rental_price_per_day, is_available)

        if engine_capacity <= 0:
            raise ValueError("engine_capacity must be greater than zero")

        if bike_type not in Bike.allowed_types:
            raise ValueError(f"bike_type must be one of {Bike.allowed_types}")

        self.engine_capacity = engine_capacity
        self.helmet_included = helmet_included
        self.bike_type = bike_type

    def calculate_rental_cost(self, number_of_days: int) -> float:
        base_cost = super().calculate_rental_cost(number_of_days)
        return base_cost + 10

    def check_license_requirement(self) -> str:
        return "License Required" if self.engine_capacity > 50 else "License Not Required"

    def add_helmet_charge(self) -> float:
        return 0 if self.helmet_included else 5

    def display_details(self):
        super().display_details()
        print(
            f"Engine Capacity: {self.engine_capacity} CC\n"
            f"Helmet Included: {self.helmet_included}\n"
            f"Bike Type: {self.bike_type}"
        )

    def __str__(self):
        return f"Bike({self.vehicle_id}, {self.brand}, {self.model}, engine={self.engine_capacity}CC)"


if __name__ == "__main__":
    try:
        car1 = Car("VEH-1001", "Toyota", "Corolla", 120, 5, "Petrol", True)
        car2 = Car("VEH-1002", "Honda", "City", 150, 4, "Diesel", False)
        bike1 = Bike("VEH-2001", "Yamaha", "R15", 60, 155, False, "Sports")
        bike2 = Bike("VEH-2002", "Bajaj", "Chetak", 45, 60, True, "Electric")

        vehicles = [car1, car2, bike1, bike2]

        print("=== VEHICLE DETAILS ===")
        for v in vehicles:
            print(v)
            v.display_details()
            print("-" * 40)

        print("\n=== RENTAL COSTS ===")
        print("Car1 for 5 days:", car1.calculate_rental_cost(5))
        print("Car2 for 7 days with discount:", car2.calculate_long_trip_discount(7))
        print("Bike1 for 3 days:", bike1.calculate_rental_cost(3))
        print("Bike2 for 4 days + helmet charge:", bike2.calculate_rental_cost(4) + bike2.add_helmet_charge())

        print("\n=== AVAILABILITY TEST ===")
        car1.rent_vehicle()
        print("Car1 available after rent:", car1.is_available)

        try:
            car1.rent_vehicle()
        except ValueError as e:
            print("Error:", e)

        car1.return_vehicle()
        print("Car1 available after return:", car1.is_available)

        print("\n=== LICENSE CHECK ===")
        print("Bike1:", bike1.check_license_requirement())
        print("Bike2:", bike2.check_license_requirement())

        print("\n=== FAMILY SUITABILITY ===")
        print("Car1 suitable for 4 seats:", car1.check_family_suitability(4))
        print("Car2 suitable for 6 seats:", car2.check_family_suitability(6))

        print("\n=== TOTAL VEHICLE COUNT ===")
        print(Vehicle.get_total_vehicle_count())

        print("\n=== INVALID TESTS ===")
        try:
            bad_car = Car("BAD-1", "X", "Y", -100, 4, "Petrol", True)
        except ValueError as e:
            print("Error:", e)

        try:
            bad_bike = Bike("VEH-3001", "X", "Y", 50, -10, True, "Sports")
        except ValueError as e:
            print("Error:", e)

        try:
            Vehicle("VEH-4001", "Test", "Model", 0)
        except ValueError as e:
            print("Error:", e)

    except Exception as e:
        print("Unexpected error:", e)