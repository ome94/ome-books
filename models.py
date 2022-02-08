from sqlalchemy import Column, Integer, String, ForeignKey, null
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Author(Base):
    __tablename__ = 'authors'

    id = Column('id', Integer, primary_key=True)
    name = Column('name', String, nullable=False)

class Book(Base):
    __tablename__ = 'books'

    id = Column('id', Integer, primary_key=True)
    title = Column('title', String, nullable=False)
    author_id = Column('author_id', ForeignKey('authors.id'))
    isbn = Column('isbn', String(10), unique=True, nullable=False)
    year = Column('year', Integer, nullable=False)

class User(Base):
        __tablename__ = 'user'

        username = Column('username', String, primary_key=True)
        password = Column('password', String, nullable=False)
        firstname = Column('firstname', String, nullable=False)
        lastname = Column('lastname', String, nullable=False)
        