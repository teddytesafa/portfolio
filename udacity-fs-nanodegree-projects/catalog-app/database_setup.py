import sys

from sqlalchemy import Column, ForeignKey, Integer, String

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.orm import relationship

from sqlalchemy import create_engine

Base = declarative_base()

###### categories ######

class User(Base):

    __tablename__ = 'user'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    picture = Column(String(250), nullable = True)
    email = Column(String(250), nullable = False)
    


class Category(Base):

    __tablename__ = 'category'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

###### items ######

class Item(Base):

    __tablename__ = 'item'

    name = Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    category_id = Column(Integer, ForeignKey('category.id'))
    user_id = Column(Integer, ForeignKey('user.id'))
    description = Column(String(250), nullable = True)

    category = relationship(Category)
    user = relationship(User)



    @property
    def serialize(self):
        return {
            'name' : self.name,
            'description' : self.description,
            'id' : self.id,
            }


###### end ######

engine = create_engine('sqlite:///catalogwithusers.db')

Base.metadata.create_all(engine)
