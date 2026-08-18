#PART A — SQLAlchemy Core Retrieval
import sqlalchemy
from sqlalchemy import create_engine, MetaData, Table, Columns, Integer, Float, String, ForeignKey
from sqlalchemy.orm import sessionmaker, declarative_base, relationship
engine = create_engine('sqlite:///example.db',echo = True)
meta = MetaData()
students = Table(
    "students",meta
    Column("id", Integer, primary_key = True),
    Column("name",String(50), nullable = False),
    Column("age", Integer)
    Column("department",String(50))
)

courses = Table(
    "courses",meta
    Column("id",Integer, ForeignKey("student.id"), primary_key = True),
    Column("id", Integer, ForeignKey("course.id"), primary_key = True),
    Column("grade", String(2))
)

enrollments = Table(
    "enrollments", meta
    Column("id",Integer, compiste_primary_key = True)
    Column("id",Ineger,ForeignKey("student.id"),primary_key = True),
    Column("id",Integer, ForeignKey("course.id"),primary_key = True)
)

meta.create_all(engine)
# INSERT
with engine.begin() as conn:
    conn.execute(students.insert().values(id = 1, name = "bob",age = 30, department = "maths"))
    conn.execute(students.insert().values(id = 2, name = "balu",age = 30, department = "english"))
    conn.execute(students.insert().values(id = 3, name = "richy",age = 30, department = "hindi"))

#2. SELECT Find students from "science".
with engine.begin() as conn:
 conn.execute(students.select().where(students.c.department == "science"))
#3. UPDATE
with engine.begin() as conn:
 conn.execute(students.update().where(students.c.department == "science").values(department = "math"))

#4. DELETE
with engine.begin() as conn:
 conn.execute(students.delete().where(students.c.department == "math"))
#5. JOIN
with engine.begin() as conn:
 conn.execute(students.join(enrollments, students.c.id == enrollments.c.students.id))





