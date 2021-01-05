import os

from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

@app.route("/")
def index():
    return render_template('index.html', title='Home')

@app.route("/login")
def login():
    return render_template('login.html', title='Login')

@app.route("/auth", methods=["POST"])
def authenticate():
    username = request.form.get('username')
    password = request.form.get('password')
    
    # TODO: validate(username, password)

    user = db.execute("SELECT * FROM users WHERE username = :username AND password = :password",
    {
        "username": username,
        "password": password
    }).fetchone()

    if user is None:
        return render_template('login.html', message="username or password incorrect")
    
    # TODO: Open Session For user
    
    return redirect(url_for('search'))

@app.route("/signup")
def signup():
    return render_template('signup.html', title='New User')

@app.route("/register", methods=["POST"])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    firstname = request.form.get('firstname')
    lastname = request.form.get('lastname')

    # validate(username, password)
    # TODO:
    # CHECKS:
    # 1. Not empty strings,
    # 2. User not already registered
    user = db.execute("SELECT username FROM users WHERE username = :username",{
        "username": username,
    }).fetchone()
    
    if user is None:
        db.execute("INSERT INTO users(firstname, lastname, username, password) VALUES(:firstname, :lastname,:username, :password)",{
            "username": username,
            "firstname": firstname,
            "lastname": lastname,
            "password": password
        })
    
        db.commit()
        return render_template('success.html')

    return redirect('signup')


@app.route("/search")
def search():
    # Restrict This Page Only To Logged In Users
    return render_template('search.html', title='Search')

@app.route("/logout")
def logout():
    return