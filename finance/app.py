import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)
d1={}
# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    ind=db.execute("SELECT * FROM users, stocks WHERE users.id=stocks.id AND users.id=?",session["user_id"])
    total=0.0
    for i in range(len(ind)):
        symb=lookup(ind[i]["symbol"])
        ind[i]["price"]=symb["price"]
        total+=symb["price"]*ind[i]["shares"]
    return render_template("index.html",titles=ind,total=total)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    c=db.execute("SELECT cash FROM users WHERE id=?", session["user_id"])
    if request.method=="POST":
        if not request.form.get("symbol") or not request.form.get("shares"):
            return apology("Incomplete/Invalid Details",203)
        symb=request.form.get("symbol").upper()
        num=request.form.get("shares")
        d1=lookup(symb)
        if isinstance(num, float) or not num.isdigit():
            return apology("Invalid Input",400)
        if int(num)<0:
            return apology("Invalid input",400)
        if d1==None:
            return apology("Invalid symbol",400)
        if (int(num)*float(d1["price"]))>c[0]["cash"]:
            return apology("Not Enough Cash", 303)
        symb1=db.execute("SELECT * FROM stocks WHERE id=? AND symbol=?",session["user_id"],symb)
        if len(symb1)==1:
            db.execute("UPDATE stocks SET shares=? WHERE symbol=? AND id=?",symb1[0]["shares"]+int(num),symb,session["user_id"])
        else:
            db.execute("INSERT INTO stocks(id, name, symbol, shares) VALUES (?,?,?,?)",session["user_id"],d1["name"], d1["symbol"],int(num))
        db.execute("UPDATE users SET cash=? WHERE id=?",c[0]["cash"]-(int(num)*float(d1["price"])),session["user_id"])
        db.execute("INSERT INTO transactions(id,name,symbol,type,shares) VALUES (?,?,?,'BUY',?)",session["user_id"],d1["name"],d1["symbol"],int(num))
        return redirect("/")
    return render_template("buy.html",cash=c)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    hist=db.execute("SELECT name,symbol,type,shares FROM transactions WHERE id=?",session["user_id"])
    return render_template("history.html",stocks=hist)
    # return apology("TODO")


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method=="GET":
        return render_template("quote.html")
    elif request.method=="POST":
        symb=request.form.get("symbol")
        d1=lookup(symb)
        if d1==None:
            return apology("Invalid Symbol", 400)
        else:
            return render_template("quoted.html", d1=d1)
    # return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method=="GET":
        return render_template("register.html")
    elif request.method=="POST":
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        user=request.form.get("username")
        pass0=request.form.get("password")
        pass1=request.form.get("confirmation")
        name=db.execute("SELECT id FROM users WHERE username=?",user)
        if len(name)==1:
            return apology("Username already taken", 400)
        if pass0!=pass1:
            return apology("Passwords do not match", 400)
        db.execute("INSERT INTO users(username, hash) VALUES(?,?)",user,generate_password_hash(pass0))
        rows=db.execute("SELECT * FROM users WHERE username=?",user)
        session["user_id"] = rows[0]["id"]
        return redirect("/")
    # return apology("TODO")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    c=db.execute("SELECT cash FROM users WHERE id=?",session["user_id"])
    st=db.execute("SELECT * FROM  stocks WHERE id=?",session["user_id"])
    if request.method=="POST":
        symb=request.form.get("symbol")
        try:
            num=int(request.form.get("shares"))
        except:
            return apology("Invalid input",400)

        if not symb or not num:
            return apology("Invalid Input",400)
        if num<=0:
            return apology("Invalid input",400)

        s1=db.execute("SELECT * FROM stocks WHERE id=? AND symbol=?",session["user_id"],symb.upper())
        if len(s1)!=1 or s1[0]["shares"]<num:
            return apology("Incorrect/Invalid Input",303)


        db.execute("UPDATE stocks SET shares = ? WHERE id = ? AND symbol = ?",s1[0]["shares"]-num,session["user_id"],symb)
        db.execute("INSERT INTO transactions(id,name,symbol,type,shares) VALUES (?,?,?,'SELL',?)",session["user_id"],s1[0]["name"],s1[0]["symbol"],num)
        price=lookup(symb)
        db.execute("UPDATE users SET cash = ? WHERE id = ?",c[0]["cash"]+(num*price["price"]),session["user_id"])
        db.execute("DELETE FROM stocks WHERE id = ? AND shares = 0",session["user_id"])
        return redirect("/")
    return render_template("sell.html",cash=c,stocks=st)

@app.route("/change", methods=["GET","POST"])
@login_required
def change():
    if request.method=="POST":
        if not (request.form.get("username") or request.form.get("password") or request.form.get("passwordc")):
            return apology("Invalid/Incorrect Input",203)
        op=request.form.get("username")
        np=request.form.get("password")
        np1=request.form.get("passwordc")
        p=db.execute("SELECT * FROM users WHERE id=?",session["user_id"])
        if np==op or np!=np1 or not check_password_hash(p[0]["hash"],op):
            return apology("Invalid/Incorrect Input",203)
        db.execute("UPDATE users SET hash=? WHERE id=?",generate_password_hash(np),session["user_id"])
        return redirect("/")
    return render_template("change.html")
    # return apology()

@app.route("/add",methods=["GET","POST"])
@login_required
def add():
    cash=db.execute("SELECT cash FROM users WHERE id=?",session["user_id"])
    if request.method=="POST":
        c=float(request.form.get("money"))
        db.execute("UPDATE users SET cash=? WHERE id=?",cash[0]["cash"]+c,session["user_id"])
        return redirect("/")
    return render_template("add.html",cash=cash)