from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import ForeignKey,Text

class Base(DeclarativeBase()):
    pass

class User(Base):
    __tablename__ = "users"

    id:Mapped[int] = mapped_column(primary_key =True)
    username:Mapped[str] = mapped_column(nullable = False)
    email_address:Mapped[str] = mapped_column(nullable = False)
    comments:Mapped[list["Comment"]] = mapped_column(back_populates = "user")

class Comment(Base):
    __tablename__ = "comments"

    id:Mapped[int] = mapped_column(primary_key = True)
    user_id:Mapped[int] = mapped_column(ForeignKey("users.id"), nullable = False)
    text:Mapped[str] = mapped_column(Text, nullable = False)