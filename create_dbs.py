import os
import csv

from sqlalchemy import Column, ForeignKey, Integer, String, Table, create_engine, MetaData
from sqlalchemy.orm import scoped_session, sessionmaker

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

metadata = MetaData()
usrs_mtdata = MetaData()

def create_authors():
    if 'authors' not in engine.table_names():
        print("Creating Authors Table...")
        authors = Table(
            'authors', db.registry,
            Column('id', Integer, primary_key=True),
            Column('name', String, nullable=False)

        )
        metadata.create_all(engine)
        print("Authors Created.")

    else:
        print('Authors table already exists')

def create_books():
    if 'books' not in engine.table_names():
        print("Creating Books Table...")
        books = Table(
            'books', db.registry,
            Column('id', Integer, primary_key=True),
            Column('title', String, nullable=False),
            Column('author_id', ForeignKey('authors.id')),
            Column('isbn', String(10), unique=True, nullable=False),
            Column('year', Integer, nullable=False)
        )

        metadata.create_all(engine)
        print("Books Created.")
        
        print()
        print('Populating Books And Authors')
        populate_table()
        print('Done')

    else:
        print('Books table already exists')

def create_users():
    if 'users' not in usrs_eng.table_names():
        user_table = Table(
            'users', usrs_mtdata,
            Column('username', String, primary_key=True),
            Column('password', String, nullable=False),
            Column('firstname', String, nullable=False),
            Column('lastname', String, nullable=False)
        )

        usrs_mtdata.create_all(usrs_eng)
        print('Users table created')
        
    else:
        print('Users table already exists.')

# TODO
# Account for the possibility of books and authors already existing.
def populate_table():
    f = open('books.csv')
    reader = csv.reader(f) # A csv reader object is returned

    # Convert the csv reader object to a list and remove the csv header
    books = [*reader][1:]

    progress = 0
    with engine.connect() as conn:
        for isbn, title, author, year in books:
            # First Check if Author Already Exists in The Authors' Table
            author_id = get_author_id(author)

            if author_id is None:
                # Record An Entry For New Author In Authors' Table
                conn.execute("INSERT INTO authors(name) VALUES (:author)", {"author": author})
                author_id = get_author_id(author)
                
            conn.execute("INSERT INTO books(title, author_id, isbn, year) VALUES (:title, :author, :isbn, :year)",
                {
                    "title": title,
                    "author": author_id.id,
                    "isbn": isbn,
                    "year": int(year)
                }
            )

            progress += 1
            print(f"{progress}/5000 - {title}")
        
        conn.commit()

def get_author_id(author):
    with engine.connect() as conn:
        author_id = conn.execute("SELECT id FROM authors WHERE name = :author", {"author": author}).fetchone()

    return author_id # A RowProxy is returned, How Can I single out the Id From This Object

def main():
    create_authors()
    create_books()
    create_users()

if __name__ == "__main__":
    main()