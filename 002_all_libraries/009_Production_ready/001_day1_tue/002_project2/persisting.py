from models import Base, User, Comment
from sqlalchemy.orm import Session
from connect import engine

session = Session(bind=engine)

user1 = User(username = "john_doe", email_address = "john.doe@example.com"
             comments = [Comment(text = "Hello, this is my first comment!"),
                         Comment(text = "SqlAlchemy is great!")])
paul = User(username = "paul_smith", email_address = "paul.smith@example.com"
             comments = [Comment(text = "I love programming!"),
                         Comment(text = "Python is my favorite language.")])

cathy = User(username = "cathy_jones", email_address = "cathy.jones@example.com"
             comments = [Comment(text = "I enjoy learning new technologies!"),
                         Comment(text = "Machine learning is fascinating.")])
Session.add_all([user1, paul, cathy])
session.commit()