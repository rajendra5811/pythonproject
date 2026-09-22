from sqlalchemy import Column, Integer, String
from database import Base
class User(Base):
    __tablename__ = "users_fastapi"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(str)
    age = Column(int)
    phone = Column(str)