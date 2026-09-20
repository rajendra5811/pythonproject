from sqlalchemy import create_engine, Column, Integer, String, MetaData, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

DATABASE_URL = "postgresql://user:password@localhost:5432/mydatabase"

engine = create_engine(DATABASE_URL, echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind = engine)
session = SessionLocal()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    age = Column(Integer)

Base.metadata.create_all(bind=engine)

#Create a User
user1 = User(name="Alice", age=30)
user2 = User(name="Bob", age=25)
session.add_all([user1, user2])
session.commit()
