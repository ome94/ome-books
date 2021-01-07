import os
import csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

print("Creating Authors Table...")
db.execute('''
    CREATE TABLE authors(
        id SERIAL PRIMARY KEY,
        name VARCHAR NOT NULL
    )
''')
print("Authors Created.")

print("Creating Books Table...")
db.execute('''
    CREATE TABLE books(
        id SERIAL PRIMARY KEY,
        title VARCHAR NOT  NULL,
        author_id INTEGER REFERENCES authors,
        isbn VARCHAR  NOT NULL UNIQUE,
        year INTEGER NOT NULL
    )
''')
print("Books Created.")

def main():
    f = open('books.csv')
    reader = csv.reader(f) # A csv reader object is returned

    # Convert the csv reader object to a list and remove the csv header
    books = list(reader)[1:]

    progress = 0
    for isbn, title, author, year in books:
        # First Check if Author Already Exists in The Authors' Table
        author_id = get_author_id(author)

        if author_id is None:
            # Record An Entry For New Author In Authors' Table
            db.execute("INSERT INTO authors(name) VALUES (:author)", {"author": author})
            author_id = get_author_id(author)
            
        db.execute("INSERT INTO books(title, author_id, isbn, year) VALUES (:title, :author, :isbn, :year)",
            {
                "title": title,
                "author": author_id.id,
                "isbn": isbn,
                "year": int(year)
            }
        )

        progress += 1
        print(f"{progress}/5000 - {title}")
    
    db.commit()

def get_author_id(author):
    author_id = db.execute("SELECT id FROM authors WHERE name = :author", {"author": author}).fetchone()
    return author_id # A RowProxy is returned, How Can I single out the Id From This Object

if __name__ == "__main__":
    main()