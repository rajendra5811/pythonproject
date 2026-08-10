#3. Student Course Management System
class Student:
   def __init__(self, student_id, name, course, fee):
       self.student_id = student_id
       self.name = name
       self.course = course
       self.fee = fee
       self.is_enrolled = False

   def display_student_info(self):
        print(f"Student ID: {self.student_id}")
        print(f"Name: {self.name}")
        print(f"Course: {self.course}")
        print(f"Fee: {self.fee}")
        print(f"Enrolled: {'Yes' if self.is_enrolled else 'No'}")

class CourseManagement(Student):
    def __init__(self, student_id, name, course, fee):
        super().__init__(student_id, name, course, fee)
        self.students = []

    def enroll_student(self, student):
        if not student.is_enrolled:
            student.is_enrolled = True
            self.students.append(student)
            print(f"Student enrolled successfully: {student.name}")
        else:
            print(f"Student is already enrolled: {student.name}")

    def cancel_enrollment(self, student):
        if student.is_enrolled:
            student.is_enrolled = False
            self.students.remove(student)
            print(f"Enrollment cancelled for student: {student.name}")
        else:
            print(f"Student is not enrolled: {student.name}")

    def update_course(self, student, new_course):
        if student.is_enrolled:
            student.course = new_course
            print(f"Course updated for student: {student.name}")
        else:
            print(f"Student is not enrolled: {student.name}")

 