from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from sqlalchemy.exc import NoResultFound
import hashlib
from create_dbs import db, usrs
from models import User

# Check for environment variable        
app = Flask(__name__)

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

@app.route("/")
def index():
    title = "Home"
    heading = "Project 1: Books"
    USER = session.get("USER")

    return render_template('index.html', title=title, heading=heading, loggedin=bool(USER), user=USER)

@app.route('/login', methods=["GET", "POST"])
def login():
    if request.method == "GET":
        title = heading = "Login"

        return check_login('login.html', title=title, heading=heading)

    username = request.form.get('username')
    password = hashlib.md5(request.form.get('password').encode()).hexdigest()
    
    # TODO: validate(username, password)
    try:
        user = usrs.query(User).filter_by(username=username, password=password).one()
    
    except NoResultFound:
        return render_template('login.html', message="username or password incorrect")
    
    # TODO: Open Session For user
    session["USER"] = user
    return redirect(url_for('search'))

@app.route('/signup', methods=["GET", "POST"])
def signup():
    if request.method == "GET":
        title = "New User"
        heading = "Sign Up"
        
        return check_login('signup.html', title=title, heading=heading)

    username = request.form.get('username')
    password = hashlib.md5(request.form.get('password').encode()).hexdigest()
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')

    # validate(username, password)
    # TODO:
    # CHECKS:
    # 1. Not empty strings,
    # 2. User not already registered
    try:
        user = usrs.query(User).filter_by(username=username).one()
        return redirect('signup')

    except NoResultFound:
        usrs.add(
            User(username=username, password=password, firstname=firstname, lastname=lastname)
        )

        usrs.commit()

    return render_template('success.html')

@app.route("/search")
def search():
    title = "Search"
    USER = session.get("USER")
    # Restrict This Page Only To Logged In Users
    if USER is None:
        return redirect(url_for('login'))

    return render_template('search.html', title=title, heading=title, user=USER)

@app.route("/results", methods=["POST"])
def results():
    title = query = request.form.get("query")
    heading = f"Results for - {query}"
    USER = session.get("USER")

    try:
        isbn = int(query[0:-1])
        stmt = f"SELECT title, name, isbn, year FROM books b JOIN authors a ON b.author_id = a.id WHERE isbn LIKE '%{isbn}%'"
        results = db.execute(stmt).fetchall() #, {
        #     "query": isbn
        # }).fetchone()
    except ValueError:
        stmt = f"SELECT title, name, isbn, year FROM books b JOIN authors a ON b.author_id = a.id WHERE title like '%{query}%' OR name LIKE '%{query}%'"
        results = db.execute(stmt).fetchall() #, {
        # "query": query
        # }).fetchone()

    return render_template('results.html', title=title, heading=heading, user=USER, results=results, query=query)

@app.route("/logout")
def logout():
    if session.get("USER"):
        del(session["USER"])
        
        return redirect(url_for('index'))
    
    return redirect(url_for('login'))

def check_login(render, title, heading):
    USER = session.get("USER")
    if USER:
        return redirect(url_for('search'))

    return render_template(render, title=title, heading=heading, user=USER)

if __name__ == "__main__":
    app.run()