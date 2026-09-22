from main import Session
from models import User, Comment

comment = Session.query(Comment).filter_by(id = 1).first()

Session.delete(comment)