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

# Dict for sources
info_sources_dict = {
    1: "World Health Organization"
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
        maintxt = db.execute("SELECT point_text FROM '1_info'")
        for i in range(0, len(maintxt)):
            maintxt[i] = maintxt[i]['point_text']
        print (maintxt)
        return render_template("info.html", level=lvl, titles=info_titles_dict, maintxt=maintxt)
    else:
        if request.form.get("continue") == "yes":
            return redirect("/question1")
        else:
            return redirect("/information")

# QUESTIONS AND VERIFICATION SECTION

@app.route("/question1", methods=["GET", "POST"])
def question1():
    if request.method == "GET":
        # Change 1 for level number, revise question_num
        q = db.execute("SELECT question FROM '1_q' WHERE q_id='1'")
        q = q[0]['question']
        print(q)
        opt = db.execute("SELECT opt1, opt2, opt3, opt4 FROM '1_q' WHERE q_id='1'")
        opt = opt[0]
        opt_list = []
        for key in opt:
            opt_list.append(opt[key])
        return render_template("question1.html", question = q, opt_list = opt_list)
    else:
        answer = db.execute("SELECT ans FROM '1_q' WHERE q_id='1'")
        answer = answer[0]['ans']
        if request.form.get("answer") == answer:
            # Change 1 for level number, revise question_num
            return redirect("/question2")
        else:
            # Change 1 for level number, revise question_num
            q = db.execute("SELECT question FROM '1_q' WHERE q_id='1'")
            q = q[0]['question']
            print(q)
            opt = db.execute("SELECT opt1, opt2, opt3, opt4 FROM '1_q' WHERE q_id='1'")
            opt = opt[0]
            opt_list = []
            for key in opt:
                opt_list.append(opt[key])
            return render_template("question1.html", question = q, opt_list = opt_list)

@app.route("/question2", methods=["GET", "POST"])
def question2():
    if request.method == "GET":
        q = db.execute("SELECT question FROM '1_q' WHERE q_id='2'")
        q = q[0]['question']
        print(q)
        opt = db.execute("SELECT opt1, opt2, opt3, opt4 FROM '1_q' WHERE q_id='2'")
        opt = opt[0]
        opt_list = []
        for key in opt:
            opt_list.append(opt[key])
        return render_template("question2.html", question = q, opt_list = opt_list)
    else:
        answer = db.execute("SELECT ans FROM '1_q' WHERE q_id='2'")
        answer = answer[0]['ans']
        if request.form.get("answer") == answer:
            # Change 1 for level number, revise question_num
            return redirect("/question3")
        else:
            # Change 1 for level number, revise question_num
            q = db.execute("SELECT question FROM '1_q' WHERE q_id='2'")
            q = q[0]['question']
            print(q)
            opt = db.execute("SELECT opt1, opt2, opt3, opt4 FROM '1_q' WHERE q_id='2'")
            opt = opt[0]
            opt_list = []
            for key in opt:
                opt_list.append(opt[key])
            return render_template("question2.html", question = q, opt_list = opt_list)

@app.route("/question3", methods=["GET", "POST"])
def question3():
    if request.method == "GET":
        q = db.execute("SELECT question FROM '1_q' WHERE q_id='3'")
        q = q[0]['question']
        print(q)
        opt = db.execute("SELECT opt1, opt2, opt3, opt4 FROM '1_q' WHERE q_id='3'")
        opt = opt[0]
        opt_list = []
        for key in opt:
            opt_list.append(opt[key])
        return render_template("question3.html", question = q, opt_list = opt_list)
    else:
        answer = db.execute("SELECT ans FROM '1_q' WHERE q_id='3'")
        answer = answer[0]['ans']
        if request.form.get("answer") == answer:
            # Change 1 for level number, revise question_num
            return redirect("/question4")
        else:
            # Change 1 for level number, revise question_num
            q = db.execute("SELECT question FROM '1_q' WHERE q_id='3'")
            q = q[0]['question']
            print(q)
            opt = db.execute("SELECT opt1, opt2, opt3, opt4 FROM '1_q' WHERE q_id='3'")
            opt = opt[0]
            opt_list = []
            for key in opt:
                opt_list.append(opt[key])
            return render_template("question3.html", question = q, opt_list = opt_list)

@app.route("/question4", methods=["GET", "POST"])
def question4():
    if request.method == "GET":
        q = db.execute("SELECT question FROM '1_q' WHERE q_id='4'")
        q = q[0]['question']
        print(q)
        opt = db.execute("SELECT opt1, opt2, opt3, opt4 FROM '1_q' WHERE q_id='4'")
        opt = opt[0]
        opt_list = []
        for key in opt:
            opt_list.append(opt[key])
        return render_template("question4.html", question = q, opt_list = opt_list)
    else:
        answer = db.execute("SELECT ans FROM '1_q' WHERE q_id='4'")
        answer = answer[0]['ans']
        if request.form.get("answer") == answer:
            # Change 1 for level number, revise question_num
            return redirect("/question5")
        else:
            # Change 1 for level number, revise question_num
            q = db.execute("SELECT question FROM '1_q' WHERE q_id='4'")
            q = q[0]['question']
            print(q)
            opt = db.execute("SELECT opt1, opt2, opt3, opt4 FROM '1_q' WHERE q_id='4'")
            opt = opt[0]
            opt_list = []
            for key in opt:
                opt_list.append(opt[key])
            return render_template("question4.html", question = q, opt_list = opt_list)

@app.route("/question5", methods=["GET", "POST"])
def question5():
    if request.method == "GET":
        q = db.execute("SELECT question FROM '1_q' WHERE q_id='5'")
        q = q[0]['question']
        print(q)
        opt = db.execute("SELECT opt1, opt2, opt3, opt4 FROM '1_q' WHERE q_id='5'")
        opt = opt[0]
        opt_list = []
        for key in opt:
            opt_list.append(opt[key])
        return render_template("question5.html", question = q, opt_list = opt_list)
    else:
        answer = db.execute("SELECT ans FROM '1_q' WHERE q_id='5'")
        answer = answer[0]['ans']
        if request.form.get("answer") == answer:
            # Change 1 for level number, revise question_num
            return redirect("/complete")
        else:
            # Change 1 for level number, revise question_num
            q = db.execute("SELECT question FROM '1_q' WHERE q_id='5'")
            q = q[0]['question']
            print(q)
            opt = db.execute("SELECT opt1, opt2, opt3, opt4 FROM '1_q' WHERE q_id='5'")
            opt = opt[0]
            opt_list = []
            for key in opt:
                opt_list.append(opt[key])
            return render_template("question5.html", question = q, opt_list = opt_list)

@app.route("/complete", methods=["GET", "POST"])
def complete():
    if request.method == "GET":
        return render_template("complete.html")
    else:
        if request.form.get("continue") == "yes":
            user_level = db.execute("SELECT level FROM users WHERE id=:uid", uid=session["user_id"])
            user_level = int(user_level[0]["level"])
            user_level += 1
            db.execute("UPDATE users SET level=:user_level WHERE id=:uid", user_level = user_level, uid=session["user_id"])
            return redirect("/")
        else:
            return redirect("/complete")