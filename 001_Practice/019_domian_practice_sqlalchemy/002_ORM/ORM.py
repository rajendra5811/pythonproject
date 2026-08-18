from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, mapped_column, relationship
engine = create_engine('sqlite:///curse.db', echo = True)
Base = declarative_base()
"__tablename__" = "students"
id = Column(Integer, primary_key = True)
name = Column(String, nullable = False)
age = Column(Integer)
Department = Column(String)
stundents = relationship("courses", back_populates = True)

"__tablename__" = "courses"
id = Column(Integer, primary_key = True)
course = Column(String, nullable = False)
grade = Column(String(2))
courses = relationship("students", back_populates = True)
Base.create_all(engine)

