import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

# Lines 11 - 20 credit CS50

# Configure application
app = Flask(__name__)

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///sanitation.db")

# Create dictionaries for the part where information is printed onto the screen.

# Dict for titles
info_titles_dict = {
    1: "Key Facts"
}

# Dict for main text
info_maintxt_dict = {
    1: ["In 2017, 45% of the global population (3.4 billion people) used a safely managed sanitation service", "31% of the global population (2.4 billion people) used private sanitation facilities connected to sewers from which wastewater was treated."],
}


@app.route("/")
def index():
    return render_template("home.html")

@app.route("/register", methods=["GET"])
def get_register():
    return render_template("register.html")

@app.route("/register", methods=["POST"])
def register():
    if len(db.execute("SELECT * FROM users WHERE username = :username", username=request.form.get("username"))) != 0:
        return "This username is already taken!"
    elif not request.form.get("username"):
        return "You did not give a username!"
    elif not request.form.get("password"):
        return "You did not give a password!"
    elif request.form.get("password")!=request.form.get("password_confirm"):
        return "Your passwords did not match!"
    else:
        # Create user in SQL database
        pwhash = generate_password_hash(request.form.get("password"))
        rows = db.execute("SELECT * from users WHERE username = :username", username=request.form.get("username"))
        if len(rows) == 0:
            db.execute("INSERT INTO users (username,hash) VALUES (:username, :hash)", username=request.form.get("username"), hash=pwhash)
            return render_template("login.html")
        else:
            return "This username is already taken!"

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    elif request.method == "POST":
        if not request.form.get("username"):
            return("You must enter a username")
        elif not request.form.get("password"):
            return("You must enter a password")
        else:
            # Validate user
            rows = db.execute("SELECT * from users WHERE username = :username", username=request.form.get("username"))
            if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
                return "Invalid username or password!"
            else:
                session["user_id"] = rows[0]["id"]
                return redirect("/")

@app.route("/instr", methods=["GET"])
def instr():
    return render_template("instructions.html")

@app.route("/logout", methods=["GET"])
def logout():

    # Log the user out
    session.clear()

    # Return user to home page
    return redirect("/")

@app.route("/delacc", methods=["GET", "POST"])
def delacc():
    #Display delete page when requested
    if request.method == "GET":
        return render_template("delacc.html")
    else:
        if request.form.get("delacc") == "yes":
            db.execute("DELETE FROM users WHERE id=:uid", uid=session["user_id"])
            session.clear()
            return redirect("/")
        else:
            return redirect("/")

@app.route("/information", methods=["GET", "POST"])
def info():
    if request.method == "GET":
        lvl = db.execute("SELECT level FROM users WHERE id=:uid", uid = session["user_id"])
        lvl = lvl[0]["level"]
        return render_template("info.html", level=lvl, titles=info_titles_dict, maintxt=info_maintxt_dict)
    else:
        if request.form.get("continue") == "yes":
            return redirect("/question1")
        else:
            return redirect("/information")

@app.route("/question1", methods=["GET", "POST"])
def question1():
    if request.method == "GET":
        # Change 1 for level number, revise question_num
        q = db.execute("SELECT question FROM '1' WHERE q_id='1'")
        q = q[0]['question']
        print(q)
        opt = db.execute("SELECT opt1, opt2, opt3, opt4 FROM '1' WHERE q_id='1'")
        opt = opt[0]
        opt_list = []
        for key in opt:
            opt_list.append(opt[key])
        answer = db.execute("SELECT ans FROM '1' WHERE q_id='1'")
        answer = answer[0]["ans"]
        print(opt_list)
        return render_template("question1.html", question = q, opt_list = opt_list, answer = answer)
    else:
        return "submitted via py"