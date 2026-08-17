import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, relationship, sessionmaker


engine = create_engine('sqlite:///example.db', echo=True)
Base = declarative_base()
Session = sessionmaker(bind=engine)
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String, unique=True)

    def __repr__(self):
        return f"<User(name='{self.name}', email='{self.email}')>"

class Person(Base):
    __tablename__ = 'persons'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship("User", back_populates="persons")

    def __repr__(self):
        return f"<Person(name='{self.name}', age='{self.age}')>"
#explain relationship vs inheritance vs back_populates 
Base.metadata.create_all(engine)

user1 = User(id = 1, name = "bob",age = 18)
user2 = User(id = 2, name = "jhon", age = 17)

session.add_all([user1, user2])
session.commit()
users =session.query(User).all()
print(users)

filtered_users = session.query(User).filter(User.age >25).all()
print(filtered_users)