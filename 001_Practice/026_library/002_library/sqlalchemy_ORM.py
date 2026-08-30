from sqlalchemy import String, ForeginKey
from sqlalchemy.orm  import ( DeclarativeBase, Mapped, mapped_column)

class Base(DeclarativeBase):
    pass
class Department(Base):
   __tablename__ = 'departments'
   department_id : Mapped[int] = mapped_column(primary_key = True)
   department_name : Mapped[str] = mapped_column(String(100))

class Student(Base):
    __tablename__ = 'students'
    student_id: Mapped[int] = mapped_column(primary_key = True)
    name : Mapped[str] = mapped_column(String(100))
    age : Mapped[int] = mapped_column(Integer(10))
    city : Mapped[str] = mapped_column(String(100))
    department_id: Mapped[int] = mapped_column(ForeignKey("departments.department_id"))