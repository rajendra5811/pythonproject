from persisting import session
from models import User, Comment
from sqlalchemy import select

stmt = select(User).where(User.username.in_(["john_doe", "paul_smith"]) )

result = session.execute(stmt).scalars().all()

for user in result:
    print(user)
