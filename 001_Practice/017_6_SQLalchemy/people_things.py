import sqlalchemy
from sqlalchemy import (
    create_engine,
    MetaData,
    Table,
    Column,
    Integer,
    String,
    Float,
    ForeignKey,
    select,
    func,
)

engine = create_engine("sqlite:///school.db", echo=True)
meta = MetaData()

people = Table(
    "people",
    meta,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("age", Integer),
)

things = Table(
    "things",
    meta,
    Column("id", Integer, primary_key=True),
    Column("name", String(50), nullable=False),
    Column("description", String, nullable=True),
    Column("price", Float),
    Column("owner_id", Integer, ForeignKey("people.id")),
)

meta.create_all(engine)

with engine.begin() as conn:
    conn.execute(people.insert().values(name="John Doe", age=30))
    conn.execute(people.insert().values(name="Alice", age=25))
    conn.execute(
        things.insert().values(
            [
                {"name": "Laptop", "description": "A powerful laptop", "price": 1200.00, "owner_id": 1},
                {"name": "Smartphone", "description": "A high-end smartphone", "price": 800.00, "owner_id": 1},
                {"name": "Tablet", "description": "A lightweight tablet", "price": 500.00, "owner_id": 2},
            ]
        )
    )

with engine.connect() as conn:
    stmt = select(people.c.name, things.c.name.label("item_name"), things.c.price).select_from(
        people.join(things, people.c.id == things.c.owner_id)
    )
    for row in conn.execute(stmt):
        print(row)

with engine.connect() as conn:
    stmt = (
        select(people.c.name, func.sum(things.c.price).label("total_price"))
        .select_from(people.join(things, people.c.id == things.c.owner_id))
        .group_by(people.c.name)
        .having(func.sum(things.c.price) > 1000)
    )
    for row in conn.execute(stmt):
        print(row)

with engine.begin() as conn:
    conn.execute(people.update().where(people.c.name == "John Doe").values(age=31))
    conn.execute(things.delete().where(things.c.name == "Tablet"))

print("SQLAlchemy script completed successfully.")
