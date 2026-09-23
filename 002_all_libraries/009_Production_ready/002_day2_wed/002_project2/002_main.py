from datetime import datetime, timezone
from typing import Optional
from sqlalchemy import create_engine, Table, Column, Integer, String, Float, MetaData,Text, ForeignKey, select
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, relationship

engine = create_engine("sqlite:///db.sqlite3", echo=True)

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
    last_login: Mapped[Optional[datetime]] = mapped_column(String(50))

    posts: Mapped[list["Post"]] = relationship(back_populates="user")

    def __repr__(self):
        return f"User(id={self.id}, name={self.name})"

class Post(Base):
    __tablename__ = "post"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100), default="Untitled Post")
    content: Mapped[str] = mapped_column(Text)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
    
    user: Mapped["User"] = relationship(back_populates="posts")

    def __repr__(self):
        return f"Post(id={self.id}, title={self.title})"

Base.metadata.create_all(engine)

with sessionmaker(engine)() as session:
    anthony = User(name="Anthony")
    kim = User(name="Kim", last_login=datetime.now(timezone.utc))
    session.add_all([anthony, kim])
    session.commit()

    post1 = Post(title="Anthony's First Post", content="This is the content of Anthony's first post.")
    post2 = Post(title="Kim's First Post", content="This is the content of Kim's first post.")
    post3 = Post(title="Kim's Second Post", content="This is the content of Kim's second post.")
    post4 = Post(title="Kim's Third Post", content="This is the content of Kim's third post.")
    post5 = Post(title="Kim's Fourth Post", content="This is the content of Kim's fourth post.")
    anthony.posts.append(post1)
    kim.posts.append(post2)
    kim.posts.append(post3)
    kim.posts.append(post4)
    kim.posts.append(post5)

    session.commit()

    statement = session.query(User)
    users = session.scalars(statement).all()
    for user in users:
        print(user)
        for post in user.posts:
            print(f"  {post}")

    # Query a specific user by ID
    anthony = session.query(User, 1)
    if anthony:
        print(f"Found user: {anthony}")

    statement = select(User).where(User.name == "Kim")
    kim = session.scalars(statement).first()
    if kim:
        print(f"Found user: {kim}")


statement = select(Post).where(Post.user_id == anthony).order_by(Post.id.desc())
posts = session.scalars(statement).all()
for post in posts:
    print(f"User: {anthony.name}, Post: {post.title}, Content: {post.content}")