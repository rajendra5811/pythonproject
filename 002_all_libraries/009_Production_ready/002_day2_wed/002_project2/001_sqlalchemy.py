from sqlalchemy import (
    create_engine,
    String,
    Column,
    Integer,
    ForeignKey
)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import relationship, sessionmaker, declarative_base


# Database configuration
engine = create_engine(
    "sqlite:///production_warehouse.db",
    echo=True
)

Base = declarative_base()

SessionLocal = sessionmaker(bind=engine)
session = SessionLocal()


# Models
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)

    tasks = relationship(
        "Task",
        back_populates="user",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}', email='{self.email}')"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    description = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    user = relationship("User", back_populates="tasks")

    def __repr__(self):
        return f"Task(id={self.id}, title='{self.title}')"


Base.metadata.create_all(engine)


# Utility functions
def get_user_by_email(email):
    return session.query(User).filter(User.email == email).first()


def get_user_by_id(user_id):
    return session.query(User).filter(User.id == user_id).first()


def get_task_by_id(task_id):
    return session.query(Task).filter(Task.id == task_id).first()


def confirm_action(prompt: str) -> bool:
    answer = input(f"{prompt} (y/n): ").strip().lower()
    return answer in ("y", "yes")


# Create operations
def add_user():
    name = input("Enter user name: ").strip()
    email = input("Enter user email: ").strip()

    if not name or not email:
        print("Name and email are required.")
        return

    if get_user_by_email(email):
        print(f"User with this email already exists: {email}")
        return

    try:
        new_user = User(name=name, email=email)
        session.add(new_user)
        session.commit()

        print(
            f"User added successfully: "
            f"{new_user.name} ({new_user.email})"
        )

    except IntegrityError:
        session.rollback()
        print("Error: Email must be unique.")


def add_task():
    email = input("Enter user email for the task: ").strip()
    user = get_user_by_email(email)

    if not user:
        print(f"No user found with email: {email}")
        return

    title = input("Enter task title: ").strip()
    description = input("Enter task description: ").strip()

    if not title:
        print("Task title is required.")
        return

    try:
        new_task = Task(
            title=title,
            description=description,
            user=user
        )

        session.add(new_task)
        session.commit()

        print(
            f"Task added successfully for user "
            f"{user.name}: {new_task.title}"
        )

    except IntegrityError:
        session.rollback()
        print("Error while adding task.")


# Read operations
def query_users():
    users = session.query(User).all()

    if not users:
        print("No users found.")
        return

    for user in users:
        print(
            f"ID: {user.id} | "
            f"Name: {user.name} | "
            f"Email: {user.email} | "
            f"Tasks: {len(user.tasks)}"
        )


def query_tasks():
    tasks = session.query(Task).all()

    if not tasks:
        print("No tasks found.")
        return

    for task in tasks:
        print(
            f"ID: {task.id} | "
            f"Title: {task.title} | "
            f"Description: {task.description} | "
            f"User: {task.user.name}"
        )


# Update operations
def update_user():
    try:
        user_id = int(input("Enter user ID: "))
    except ValueError:
        print("Invalid user ID.")
        return

    user = get_user_by_id(user_id)

    if not user:
        print("User not found.")
        return

    new_name = input(
        f"Enter new name [{user.name}]: "
    ).strip()

    new_email = input(
        f"Enter new email [{user.email}]: "
    ).strip()

    if new_name:
        user.name = new_name

    if new_email and new_email != user.email:
        existing_user = get_user_by_email(new_email)

        if existing_user:
            print("Another user already has this email.")
            return

        user.email = new_email

    try:
        session.commit()
        print("User updated successfully.")

    except IntegrityError:
        session.rollback()
        print("Could not update user.")


def update_task():
    try:
        task_id = int(input("Enter task ID: "))
    except ValueError:
        print("Invalid task ID.")
        return

    task = get_task_by_id(task_id)

    if not task:
        print("Task not found.")
        return

    new_title = input(
        f"Enter new title [{task.title}]: "
    ).strip()

    new_description = input(
        f"Enter new description [{task.description}]: "
    ).strip()

    if new_title:
        task.title = new_title

    if new_description:
        task.description = new_description

    session.commit()
    print("Task updated successfully.")


# Delete operations
def delete_user():
    try:
        user_id = int(input("Enter user ID: "))
    except ValueError:
        print("Invalid user ID.")
        return

    user = get_user_by_id(user_id)

    if not user:
        print("User not found.")
        return

    if confirm_action(
        f"Delete user '{user.name}' and all related tasks?"
    ):
        session.delete(user)
        session.commit()
        print("User deleted successfully.")
    else:
        print("Deletion cancelled.")


def delete_task():
    try:
        task_id = int(input("Enter task ID: "))
    except ValueError:
        print("Invalid task ID.")
        return

    task = get_task_by_id(task_id)

    if not task:
        print("Task not found.")
        return

    if confirm_action(f"Delete task '{task.title}'?"):
        session.delete(task)
        session.commit()
        print("Task deleted successfully.")
    else:
        print("Deletion cancelled.")


# Main menu
def main():
    actions = {
        "1": add_user,
        "2": add_task,
        "3": query_users,
        "4": query_tasks,
        "5": update_user,
        "6": update_task,
        "7": delete_user,
        "8": delete_task,
    }

    while True:
        print(
            "\nOptions:\n"
            "1. Add User\n"
            "2. Add Task\n"
            "3. Query Users\n"
            "4. Query Tasks\n"
            "5. Update User\n"
            "6. Update Task\n"
            "7. Delete User\n"
            "8. Delete Task\n"
            "9. Exit"
        )

        choice = input("Select an option: ").strip()

        if choice == "9":
            print("Goodbye!")
            break

        action = actions.get(choice)

        if action:
            action()
        else:
            print("Invalid option. Please try again.")


if __name__ == "__main__":
    try:
        main()
    finally:
        session.close()