from models import Base, User, Comment
from connect import engine

print("Creating tables >>>")
Base.metadata.create_all(bind = engine)
print("Tables created successfully!")