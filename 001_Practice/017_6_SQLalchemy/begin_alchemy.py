#import sqlalchemy 
#print("sqlalchemy version:", sqlalchemy.__version__) 
# sqlalchemy version: 2.0.52 
import sqlalchemy 
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, ForeignKey
engine = create_engine("sqlite:///school.db", echo=True)
meta = MetaData()
people = Table(
    "people", meta,
    Column("id", Integer, primary_key=True),
    Column("name", String(50)),
    Column("age", Integer)
)
meta.create_all(engine)
