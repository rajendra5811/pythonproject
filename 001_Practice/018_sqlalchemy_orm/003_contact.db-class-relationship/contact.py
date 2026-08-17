from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, create_engine,float, DateTime
from sqlalchemy.orm import relationship, declarative_base, sessionmaker

engine = create_engine('sqlite:///contacts.db', echo=True)

Base = declarative_base()

class Contact(Base):
    __tablename__ = 'contacts'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    created_at = Column(DateTime)

    def __repr__(self):
        return f"<Contact(name='{self.name}', email='{self.email}', phone='{self.phone}', address='{self.address}')>"
class person(Base):
    __tablename__ = 'persons'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    email = Column(String)
    phone = Column(String)
    address = Column(String)
    created_at = Column(DateTime)

    def __repr__(self):
        return f"<Person(name='{self.name}', email='{self.email}', phone='{self.phone}', address='{self.address}')>"

    persons = relationship("Thing", back_populates="person")
class Thing(Base):
    __tablename__ = 'things'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    description = Column(String)
    contact_id = Column(Integer, ForeignKey('contacts.id'))
    contact = relationship("Contact", back_populates="things")

    def __repr__(self):
        return f"<Thing(name='{self.name}', description='{self.description}', contact_id='{self.contact_id}')>"

Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)()
session = Session()

new_contact = Contact(name='John Doe', email='john.doe@example.com', phone='123-456-7890', address='123 Main St')   
new_person = person(name='Jane Smith', email='jane.smith@example.com', phone='098-765-4321', address='456 Oak Ave')
new_thing = Thing(name='Sample Thing', description='This is a sample thing.', contact=new_contact)
session.add(new_contact)
session.add(new_person)
session.flush()
session.add(new_thing)

session.commit()
print(new_person.thing)
