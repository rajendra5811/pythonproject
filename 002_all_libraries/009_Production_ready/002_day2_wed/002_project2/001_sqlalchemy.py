from sqlalchemy import create_engine, String, Float, Column, Integer,ForeignKey
from sqlalchemy.orm import relationship, sessionmaker, declarative_base


engine = create_engine("sqlite:///production_warehouse.db", echo=True)
Base = declarative_base()
Session = sessionmaker(bind = engine)
session = Session()

#Define Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True)
    tasks = relationship('Task', back_populates='user', cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"))
    user = relationship("User", back_populates="tasks")

Base.metadata.create_all(engine)

# Utility functions
def  get_user_by_email(email):
    return session.query(User).filter(User.email == email).first()

def confirm_action(prompt: str) -> bool:
    return input(f"{prompt} (y/n): ").strip().lower() == 'yes'

#CRUD operations
def add_user():
    name = input("Enter user name: ")
    email = input("Enter user email: ")
    if get_user_by_email(email):
        print(f"User with this email already exists: ({email})")
        return
   try:
        new_user = User(name=name, email=email)
        session.add(new_user)
        session.commit()
        print(f"User added successfully: {new_user.name} ({new_user.email})")
    except IntegrityError as e:
        session.rollback()
        print(f"Error adding user: {e}")

def add_task():
    email = input("Enter user email for the task: ")
    user = get_user_by_email(email)
    if not user:
        print(f"No user found with email: {email}")
        return
    title = input("Enter task title: ")
    description = input("Enter task description: ")
    new_task = Task(title=title, description=description, user=user)
    session.add(new_task)
    session.commit()
    print(f"Task added successfully for user {user.name}: {new_task.title}")

# Main Operations
