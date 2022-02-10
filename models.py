import os
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()
Usr_Base = declarative_base()

class Author(Base):
    __tablename__ = 'authors'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String, nullable=False)

    books = relationship("Book")

class Book(Base):
    __tablename__ = 'books'

    title = Column('title', String, nullable=False)
    author_id = Column('author_id', ForeignKey('authors.id'))
    isbn = Column('isbn', String(10), primary_key=True, unique=True, nullable=False)
    year = Column('year', Integer, nullable=False)

    author = relationship("Author")

class User(Usr_Base):
        __tablename__ = 'users'

        username = Column('username', String, primary_key=True)
        password = Column('password', String, nullable=False)
        firstname = Column('firstname', String, nullable=False)
        lastname = Column('lastname', String, nullable=False)
