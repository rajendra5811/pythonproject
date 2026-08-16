import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey, select

engine = create_engine("sqlite:///school.db", echo=True)
meta = MetaData()

students = Table(
    "students",
    meta,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("age", Integer),
    Column("department", String(50)),
)

courses = Table(
    "courses",
    meta,
    Column("id", Integer, primary_key=True),
    Column("course_name", String(100), nullable=False),
    Column("credit_hours", Integer),
)

enrollments = Table(
    "enrollments",
    meta,
    Column("student_id", Integer, ForeignKey("students.id"), primary_key=True),
    Column("course_id", Integer, ForeignKey("courses.id"), primary_key=True),
    Column("grade", String(2)),
)

meta.create_all(engine)

with engine.begin() as conn:
    conn.execute(students.insert().values(name="Alice", age=20, department="CS"))
    conn.execute(students.insert().values(name="Bob", age=22, department="Math"))

    conn.execute(courses.insert().values(course_name="SQLAlchemy", credit_hours=3))
    conn.execute(courses.insert().values(course_name="Python", credit_hours=4))

    conn.execute(enrollments.insert().values(student_id=1, course_id=1, grade="A"))
    conn.execute(enrollments.insert().values(student_id=2, course_id=2, grade="B"))

with engine.connect() as conn:
    result = conn.execute(
        select(students.c.name, courses.c.course_name, enrollments.c.grade)
        .select_from(
            students.join(enrollments, students.c.id == enrollments.c.student_id).join(
                courses, courses.c.id == enrollments.c.course_id
            )
        )
    )
    for row in result:
        print(row)

with engine.begin() as conn:
    conn.execute(students.update().where(students.c.name == "Alice").values(age=21))
    conn.execute(enrollments.delete().where(enrollments.c.student_id == 2))

print("Student domain example completed successfully.")
