import os
import csv
from sqlalchemy import create_engine
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import scoped_session, sessionmaker
from models import Author, Book, Base, Usr_Base

# Check for environment variable
if not os.getenv("DATABASE_URL") or not os.getenv("HEROKU_POSTGRESQL_IVORY_URL"):
    if not os.getenv("DATABASE_URL"):
        raise RuntimeError("DATABASE_URL is not set")

    elif not os.getenv("HEROKU_POSTGRESQL_IVORY_URL"):
        raise RuntimeError("HEROKU_POSTGRESQL_IVORY_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))
usrs_eng = create_engine(os.getenv("HEROKU_POSTGRESQL_IVORY_URL"))
usrs = scoped_session(sessionmaker(bind=usrs_eng))

if not ("books" in engine.table_names() or "authors" in engine.table_names()):
    Base.metadata.create_all(engine)
else:
    Base.metadata.bind = engine

if "users" not in usrs_eng.table_names():
    Usr_Base.metadata.create_all(usrs_eng)
else:
    Usr_Base.metadata.bind = usrs_eng

# TODO
# Account for the possibility of books and authors already existing.
def populate_table():
    f = open('books.csv')
    reader = csv.reader(f) # A csv reader object is returned

    # Convert the csv reader object to a list and remove the csv header
    books = [*reader][1:]

    progress = 0

    books_to_add = []
    for isbn, title, author, year in books:
        # First Check if Author Already Exists in The Authors' Table
        try:
            db.query(Author).filter_by(name=author).one()

        # Record An Entry For New Author In Authors' Table
        except NoResultFound:
            db.add(Author(name=author))
            print('New Author: {author} Added')

        finally:
            author_id = db.query(Author).filter_by(name=author).one().id
            try:
                db.query(Book).filter_by(title=title, author_id=author_id)
                print('Book {title} already exists')
            
            except NoResultFound:
                books_to_add.append(Book(isbn=isbn, title=title, author_id=author_id, year=year))
            
        progress += 1
        print(f"{progress}/5000 - {title}")
        
    if books_to_add:
        db.add_all(books_to_add)
        db.commit()
    
def main():
    populate_table()

if __name__ == "__main__":
    main()