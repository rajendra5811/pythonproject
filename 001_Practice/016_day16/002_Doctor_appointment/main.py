#12. Doctor Appointment Management
class Doctor:
    def __init__(self, doctor_id, name, specialization, consultation_fee):
        self.doctor_id = doctor_id
        self.name = name
        self.specialization = specialization
        self.consultation_fee = consultation_fee
        self.is_available = True

    def display_doctor_info(self):
        print(f"Doctor ID: {self.doctor_id}")
        print(f"Name: {self.name}")
        print(f"Specialization: {self.specialization}")
        print(f"Consultation Fee: ${self.consultation_fee}")
        print(f"Availability: {'Available' if self.is_available else 'Not Available'}")

    def update_consultation_fee(self, new_fee):
        self.consultation_fee = new_fee
        print(f"Consultation fee updated to ${self.consultation_fee} for Dr. {self.name}.")

class AppointmentManagement(Doctor):
    def __init__(self, doctor_id, name, specialization, consultation_fee):
        super().__init__(doctor_id, name, specialization, consultation_fee)
        self.appointments = []

    def book_appointment(self, patient_name):
        if self.is_available:
            self.appointments.append(patient_name)
            self.is_available = False
            print(f"Appointment booked for {patient_name} with Dr. {self.name}.")
        else:
            print(f"Dr. {self.name} is not available for appointments.")

    def cancel_appointment(self, patient_name):
        if patient_name in self.appointments:
            self.appointments.remove(patient_name)
            self.is_available = True
            print(f"Appointment for {patient_name} has been canceled.")
        else:
            print(f"No appointment found for {patient_name}.")
doctor1 = AppointmentManagement(1, "Dr. Smith", "Cardiology", 150)
doctor1.display_doctor_info()
doctor1.book_appointment("John Doe")
doctor1.display_doctor_info()
doctor1.cancel_appointment("John Doe")
doctor1.display_doctor_info()
