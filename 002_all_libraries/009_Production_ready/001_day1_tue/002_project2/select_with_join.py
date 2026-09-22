from main import Session
from models import User, Comment
from  sqlalchemy import select

statement = select(Comment).join(Comment.user).where(User.username == "jona").where(Comment.text == 'Hello World')

result = Session.execute(statement).one()

print(result)