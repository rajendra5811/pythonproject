from sqlalchemy import create_engine, String, Integer, Column, ForeignKey, Sequence
from sqlalchemy.orm import relationship, sessionmaker, declarative_base

engine = create_engine("sqlite:///orm.db", echo=True)

Session = sessionmaker(bind = engine)
session = Session()

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, Sequence('user_id_seq'), primary_key=True)
    name = Column(String(50))
    email = Column(String(100))

   posts = relationship("Post", back_populates="user")

    def __repr__(self):
        return f"User(id={self.id}, name='{self.name}', email='{self.email}')"

class Post(Base):
    __tablename__ = "posts"
    id = Column(Integer, primary_key=True)
    title = Column(String(100))
    content = Column(String(255))
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="posts")

Base.metadata.create_all(engine)

user1 = User(name="Alice", email="alice@example.com")
user2 = User(name="Bob", email="bob@example.com")
post1 = Post(title="First Post", content="This is Alice's first post.", user=user1)
post2 = Post(title="Second Post", content="This is Bob's first post.", user=user2)
post3 = Post(title="Third Post", content="This is Alice's second post.", user=user1)
session.add_all([user1, user2, post1, post2, post3])
session.commit()

posts_with_users = session.query(Post, User).join(User).all()

for post, user in posts_with_users:
    print(f"Post Title: {post.title}, Author: {user.name}, Email: {user.email}")

alice = session.query(User).filter_by(name="Alice").first()
for post in alice.posts:
    print(f"Post Title: {post.title}")

filtered_posts = session.query(Post).filter(Post.title.like("%First%")).all()

for post in filtered_posts:
    print(f"Filtered Post Title: {post.title}, Author: {post.user.name}")