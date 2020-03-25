import os

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # Determines current user
    current_user = session["user_id"]

    # Retrieve data to populate a table of currently owned shares
    stocks = db.execute("""SELECT symbol, SUM(num_shares_purchased), SUM(num_shares_sold)
    FROM portfolio WHERE user = :user GROUP BY symbol
    HAVING SUM(num_shares_purchased) > SUM(num_shares_sold)""",
                        user=current_user)

    # If user has no stocks, display blank index
    if len(stocks) == 0 or stocks == None:
        return render_template("index.html")

    else:

        # Create variable to track total value of all holdings plus cash
        grand_total = 0

        # Iterate over data retrieved from database
        for i in range(len(stocks)):

            # Determine number of shares currently owned
            # Use error catching in case no shares of that stock have ever been sold
            # Can't use subtraction when one value type is NULL
            try:
                num_owned = int(stocks[i]['SUM(num_shares_purchased)']) - int(stocks[i]['SUM(num_shares_sold)'])
            except:
                num_owned = stocks[i]['SUM(num_shares_purchased)']

            if num_owned == 0:
                continue

            # Add new key value pair to the dict for # of shares currently owned
            stocks[i]['num_owned'] = num_owned

            # Look up current price of stock
            lookup_info = lookup(stocks[i]['symbol'])
            price = lookup_info['price']

            # Add new key value pair for current price
            stocks[i]['price'] = price

            # Determine value of holdings in this stock
            value = usd(num_owned * price)

            # Add new key value paur for value of holdings
            stocks[i]['value'] = value

            # Add value to grand_total
            grand_total = grand_total + (num_owned * price)

        # Look up user's current cash balance
        raw_cash = db.execute("SELECT cash FROM users WHERE id = :user", user=current_user)

        # Define current_cash and convert to usd format
        current_cash = raw_cash[0]['cash']

        # Add current cash to grand total
        grand_total = grand_total + current_cash

        # Render the homepage
        return render_template("index.html", stocks=stocks, symbol=stocks[i]['symbol'], num_owned=stocks[i]['num_owned'],
                               price=stocks[i]['price'], value=stocks[i]['value'], current_cash=usd(current_cash), grand_total=usd(grand_total))


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "GET":
        return render_template("buy.html")

    if request.method == "POST":
        quote = lookup(request.form.get("symbol"))

        # Ensure the symbol is valid
        if quote == None:
            return apology("symbol is not valid", 400)

        # Ensure number of shares is a positive integer
        try:
            shares = int(request.form.get("shares"))
            if shares < 1:
                return apology("# of Shares must be a positive integer", 400)
        except ValueError:
            return apology("# of Shares must be a positive integer", 400)

        # Ensure user has sufficient cash to purchase the shares
        price = quote['price'] * shares
        current_user = session["user_id"]
        available_cash = db.execute("SELECT cash FROM users WHERE id=:current_user", current_user=current_user)
        if price > available_cash[0]["cash"]:
            return apology("You have insufficient funds", 403)

        # Add purchased shares to user's portfolio
        else:
            symbol = request.form.get('symbol').upper()
            print(symbol)
            db.execute("""INSERT INTO portfolio (user, symbol, num_shares_purchased, price_purchased, num_shares_sold, time_sold)
            VALUES (:current_user, :symbol, :shares, :price, :num_shares_sold, NULL)""",
                       current_user=current_user, symbol=symbol, shares=shares, price=price, num_shares_sold=0)

            # update amount of user's cash
            db.execute("UPDATE users SET cash = cash - :price WHERE id=:current_user", price=price, current_user=current_user)

            # Redirect user to home page
            return redirect("/")


@app.route("/check", methods=["GET"])
def check():
    """Return true if username available, else false, in JSON format"""
    username = request.args.get("username")
    test = db.execute("SELECT username FROM users WHERE username=:username", username=username)
    if len(test) == 0:
        return jsonify(True)
    else:
        return jsonify(False)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # determines current user
    current_user = session["user_id"]

    # Retrieve data to populate a table of currently owned shares
    transactions = db.execute("""SELECT symbol, num_shares_purchased, price_purchased, time_purchased,
    num_shares_sold, price_sold, time_sold FROM portfolio WHERE user = :user""",
                              user=current_user)

    # Check if there are no transactions to display in history
    if len(transactions) == 0:
        return render_template("history.html")

    # Determine whether each transaction was a purchase or a sale
    for i in range(len(transactions)):
        if transactions[i]['num_shares_purchased'] > 0:
            transactions[i]['transaction_type'] = 'Purchase'
            transactions[i]['price'] = usd(transactions[i]['price_purchased'])
            transactions[i]['num_shares'] = transactions[i]['num_shares_purchased']
            transactions[i]['date_time'] = transactions[i]['time_purchased']
        else:
            transactions[i]['transaction_type'] = 'Sale'
            transactions[i]['price'] = usd(transactions[i]['price_sold'])
            transactions[i]['num_shares'] = transactions[i]['num_shares_sold']
            transactions[i]['date_time'] = transactions[i]['time_sold']

    # Render the homepage
    return render_template("history.html", transactions=transactions, symbol=transactions[i]['symbol'], transaction_type=transactions[i]['transaction_type'],
                           price=transactions[i]['price'], num_shares=transactions[i]['num_shares'], date_time=transactions[i]['date_time'])


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

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

    if request.method == "GET":
        return render_template("quote.html")

    if request.method == "POST":
        quote = lookup(request.form.get("symbol"))

        # Ensure the symbol is valid
        if quote == None:
            return apology("symbol is not valid", 400)
        else:
            return render_template("quoted.html", name=quote['name'], price=usd(quote['price']), symbol=quote['symbol'])


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 400)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 400)

        # Ensure password contains at least one number and symbol
        elif request.form.get("password").isalnum() or request.form.get("password").isalpha():
            return apology("password must contain a number and symbol")

        # Ensure confirmation field was submitted
        elif not request.form.get("confirmation"):
            return apology("must confirm password", 400)

        # Ensure password and confirmation match
        if request.form.get("password") != request.form.get("confirmation"):
            return apology("passwords must match", 400)

        # Hash password
        hash = generate_password_hash(request.form.get("password"))

        # Add username to database
        rows = db.execute("INSERT INTO users (username, hash) VALUES (:username, :hash)",
                          username=request.form.get("username"), hash=hash)

        # Apologize to user if username is already taken
        if rows == None:
            return apology("username is taken", 400)

        # Remember which user has logged in
        session["user_id"] = rows

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("register.html")


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""
    if request.method == "GET":

        # Determines current user
        current_user = session["user_id"]

        # Retrieve data to populate a table of currently owned shares
        stocks = db.execute("""SELECT symbol, SUM(num_shares_purchased), SUM(num_shares_sold)
        FROM portfolio WHERE user = :user GROUP BY symbol
        HAVING SUM(num_shares_purchased) > SUM(num_shares_sold)""",
                            user=current_user)

        # Iterate over data retrieved from database
        for i in range(len(stocks)):
            print(stocks)

        return render_template("sell.html", stocks=stocks, symbol=stocks[i]['symbol'])

    if request.method == "POST":
        quote = lookup(request.form.get("symbol"))

        # Ensure the symbol is valid
        if quote == None:
            return apology("symbol is not valid", 400)

        # Ensure number of shares is a positive integer
        try:
            shares = int(request.form.get("shares"))
            if shares < 1:
                return apology("# of Shares must be a positive integer", 400)
        except ValueError:
            return apology("# of Shares must be a positive integer", 400)

        # Ensure user has sufficient shares to sell the number of shares selected
        current_user = session["user_id"]
        raw_stocks = db.execute("SELECT symbol, SUM(num_shares_purchased), SUM(num_shares_sold) FROM portfolio WHERE user = :user GROUP BY symbol",
                                user=current_user)

        # Determine nymber of shares currently owned
        # Use error catching in case no shares of that stock have ever been sold
        # Can't use subtraction when one value type is NULL
        try:
            num_owned = (raw_stocks[0]['SUM(num_shares_purchased)'] - raw_stocks[0]['SUM(num_shares_sold)'])
        except:
            num_owned = raw_stocks[0]['SUM(num_shares_purchased)']

        # Test whether user owns sufficeint shares to be sold
        if num_owned < shares:
            return apology("You don't own enough shares to sell that amount", 400)

        # Delete sold shares from user's portfolio
        else:
            symbol = request.form.get('symbol').upper()

            price = quote['price'] * shares
            db.execute("""INSERT INTO portfolio (user, symbol, num_shares_sold, price_sold, num_shares_purchased, time_purchased)
            VALUES (:current_user, :symbol, :shares, :price, :num_shares_purchased, NULL)""",
                       current_user=current_user, symbol=symbol, shares=shares, price=price, num_shares_purchased=0)

            # update amount of user's cash by amount sold
            db.execute("UPDATE users SET cash = cash + :price WHERE id=:current_user", price=price, current_user=current_user)

            # Redirect user to home page
            return redirect("/")


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
