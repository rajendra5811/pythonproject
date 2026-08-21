def transform_students(students):
    cleaned_students = []

    required_fields = [
        "student_id",
        "name",
        "age",
        "city",
        "marks"
    ]

    for student in students:

        valid = True

        for field in required_fields:
            if field not in student:
                print(
                    f"Skipping student. "
                    f"Missing field: {field}"
                )
                valid = False
                break

        if not valid:
            continue

        student["name"] = student["name"].strip().title()
        student["city"] = student["city"].strip().title()

        marks = student["marks"]

        if marks >= 90:
            student["grade"] = "A"
        elif marks >= 80:
            student["grade"] = "B"
        elif marks >= 70:
            student["grade"] = "C"
        elif marks >= 60:
            student["grade"] = "D"
        else:
            student["grade"] = "F"

        cleaned_students.append(student)

    return cleaned_students