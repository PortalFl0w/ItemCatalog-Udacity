# Imports
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine


# First we will declare the classes for the database
print "Creating Database..."

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    gid = Column(String(1000), nullable=False)
    username = Column(String(250), nullable=False)
    picture = Column(String(1000))
    email = Column(String(250))

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'username':self.username,
           'id':self.id,
           'gid':self.gid,
           'picture':self.picture,
           'email':self.email,
       }

class Category(Base):
    __tablename__ = 'category'

    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    owner_id = Column(Integer, ForeignKey('users.id'))

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name':self.name,
           'id':self.id,
           'owner_id':self.owner_id,
       }

class Item(Base):
    """
    Item class contains data about the items in the product catalogue
    """
    __tablename__ = 'item'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    description = Column(String(250))
    price = Column(String(8))
    category_id = Column(Integer,ForeignKey('category.id'))
    category = relationship(Category)
    owner_id = Column(Integer, ForeignKey('users.id'))

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'              : self.name,
           'description'       : self.description,
           'id'                : self.id,
           'price'             : self.price,
           'category_id'       : self.category_id,
           'owner_id'          : self.owner_id,
       }

engine = create_engine('sqlite:///items.db')

Base.metadata.create_all(engine) # Create Database
