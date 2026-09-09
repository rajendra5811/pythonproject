from sqlalchemy import create_engine, String, Integer
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker
from typing import List

# 1. Define the Declarative Base for ORM models
class Base(DeclarativeBase):
    pass

# 2. Define a Table Model using modern Mapped annotations
class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    age: Mapped[int] = mapped_column(Integer, nullable=True)

    def __repr__(self) -> str:
        return f"<User(id={self.id}, username='{self.username}')>"

# 3. Create the database engine (using local SQLite for lightweight demo)
engine = create_engine("sqlite:///local_warehouse.db", echo=False)

# Create all tables registered under Base in the database
Base.metadata.create_all(engine)

# 4. Factory for creating database sessions (Unit of Work)
SessionLocal = sessionmaker(bind=engine)

def insert_and_query_user(name: str, user_age: int) -> None:
    """Demonstrate transactional session lifecycle."""
    # Open a session context
    with SessionLocal() as session:
        try:
            # Create a Python object instance mapped to the table row
            new_user = UserModel(username=name, age=user_age)
            
            # Add to session workspace (stages the insert)
            session.add(new_user)
            
            # Commit the transaction to persist changes
            session.commit()
            print(f"Successfully committed user: {new_user}")
            
        except Exception as e:
            session.rollback()
            print(f"Transaction failed, rolled back: {e}")
            raise e

    # Query records back out
    with SessionLocal() as session:
        # Querying using ORM syntax
        users: List[UserModel] = session.query(UserModel).all()
        print("All users in database:", users)

# Example execution simulation
if __name__ == "__main__":
    insert_and_query_user("data_engineer_alex", 28)