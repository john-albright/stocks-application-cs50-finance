import os
import locale  # added for formatting currency
import requests  # added for AJAX request
import re  # added for regex

from dotenv import load_dotenv
load_dotenv()

# cs50 import statement 
from cs50 import SQL

# flask specific import statements
from flask import Flask, flash, redirect, render_template, request, session, jsonify  # jsonify was added here
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

# imports from helpers.py file
from helpers import apology, login_required, lookup, usd

from datetime import datetime  # added to get date & time

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

# Code to see locale options
# for lang in locale.windows_locale.values():
#     print(lang)

# Set locale for USD currency format
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""

    # print(datetime.now())

    # Find the user ID of the current user
    userID = session["user_id"]

    # Query all the transactions of the user
    transactions = db.execute("SELECT SUM(shares_count) total_shares, stock_symbol \
                              FROM (SELECT * FROM transactions WHERE user_id = ? AND stock_symbol != ?) GROUP BY stock_symbol",
                              userID, "DEPOSIT")

    # print(transactions)

    # Set variable to be summed over
    grandStockTotal = 0

    # Iterate through the total shares for each stock type
    # Transaction is a dictionary with the keys "total_shares"and "stock_symbol"
    # Add more information about each stock type to the dictionaries
    for transaction in transactions:
        # print(transaction)

        dictLookup = lookup(transaction["stock_symbol"])

        # Find the company's name given the symbol for the transaction aggregate row
        # Add a "company_name" key
        transaction["company_name"] = dictLookup["name"]

        # Find the CURRENT price of the stock
        currentPrice = dictLookup["price"]

        # Add a "current_stock_price" key
        transaction["current_stock_price"] = locale.currency(currentPrice, grouping=True)

        # Calculate the total value of the stocks
        totalStockValue = currentPrice * transaction["total_shares"]

        # Add a "total_stock_value" key
        transaction["total_stock_value"] = locale.currency(totalStockValue, grouping=True)

        # Update the grand total of stocks
        grandStockTotal += totalStockValue

        # print(transaction)
        # print(totalStockValue, grandStockTotal)

    # Get total cash available in the user's account
    totalCash = db.execute("SELECT cash FROM users WHERE id=?", userID)[0]["cash"]

    grandStockTotal += totalCash

    # Format the cash and total values as currencies to be viewed in the table
    cash = locale.currency(totalCash, grouping=True)
    total = locale.currency(grandStockTotal, grouping=True)

    return render_template("index.html", transactions=transactions, cash=cash)


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":

        symbol = request.form.get("symbol")
        shares = request.form.get("shares")

        # Check if the symbol input is blank
        if not symbol:
            return apology("No symbol was entered.")

        # Check fi the shares input is blank
        if not shares:
            return apology("No shares amount was entered.")

        # Convert shares to an integer
        try:
            shares = int(shares)
        except ValueError:
            return apology("A valid integer amount of shares must be entered.")

        # Check if the shares input is not a positive integer
        if shares < 1:
            return apology("The shares amount must be 1 or more.")

        # Convert symbol to all uppercase
        symbol = symbol.upper()

        # Search for the symbol
        dictLookup = lookup(symbol)

        # Check if the symbol input does not exist
        if not dictLookup:
            statement = "The symbol \"" + symbol + "\" does not exist."
            return apology(statement)

        # Extract information about the stock
        companyName = dictLookup["name"]
        stockPrice = dictLookup["price"]

        # Get the user's ID
        userID = session["user_id"]
        # print(userID)

        # Store the amount of cash the user has
        totalCash = db.execute("SELECT cash FROM users WHERE id=?", userID)[0]["cash"]

        # Check to see if the user can afford the stock purchase
        totalCost = stockPrice * shares

        if totalCost > totalCash:
            return apology("The user does not have sufficient funds to make the purchase.")

        # Calculate account balance
        balance = totalCash - totalCost

        # Account for errors in floating-point subtraction
        balance = (int(balance * 100)) / 100

        # print(f"\ntotal cash: {totalCash}")
        # print(f"total cost: {totalCost}")
        # print(f"balance after purchase: {balance}\n")

        # Update the cash amount in the users table
        db.execute("UPDATE users SET cash=? WHERE id=?", balance, userID)

        # Get the current date & time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Store the transaction data in the transactions table
        db.execute("INSERT INTO transactions(user_id, stock_symbol, shares_count, cost, time) VALUES(?, ?, ?, ?, ?)",
                   userID, symbol, shares, stockPrice, now)

        # Flash the message to be passed to the index page
        flash(f"{shares} {symbol} share(s) purchased!")

        # Return the user back to the index page
        return redirect("/")
    else:
        return render_template("buy.html")


@app.route("/deposit", methods=["GET", "POST"])
def deposit():
    """Allow user to add cash."""

    if request.method == "POST":
        # Extract cash amount from the form
        dollarsToAdd = request.form.get("deposit amount")

        # Check if the cash is a float
        try:
            dollarsToAdd = float(dollarsToAdd)
        except TypeError:
            return apology("A valid currency number should be entered.")

        # Make sure the number entered is accurate to the nearest thousandths place
        thousandFold = dollarsToAdd * 1000
        remainder = thousandFold % 10

        print(dollarsToAdd, remainder)

        # Check if the cash is properly formatted
        if remainder != 0:
            return apology("A valid currency amount to the nearest hundredths place must be entered.")

        # Get the user's current balance
        userID = session["user_id"]
        currentCash = db.execute("SELECT cash FROM users WHERE id=?", userID)[0]["cash"]

        # Calculate the total cash after the deposit
        updatedCash = currentCash + dollarsToAdd

        # Account for errors in floating-point addition
        updatedCash = (int(updatedCash * 100)) / 100

        # Check totals before updating tables
        print("\ncurrent cash: %f\nmoney added: %f\nupdated cash: %f\n" % (currentCash, dollarsToAdd, updatedCash))

        # return apology("Test before updating finance.db tables")

        # Update the cash balance
        db.execute("UPDATE users SET cash=? WHERE id=?", updatedCash, userID)

        # Get the current time
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Add the deposit to the transactions table
        db.execute("INSERT INTO transactions(user_id, stock_symbol, cost, shares_count, time) VALUES(?, ?, ?, ?, ?)",
                   userID, "DEPOSIT", dollarsToAdd, 0, now)

        # Flash the message to be passed to the index page
        flash(f"${dollarsToAdd:,.2f} deposited!")

        return redirect("/")
    else:
        # Get the user's ID
        userID = session["user_id"]

        # Get the user's current balance
        currentCash = db.execute("SELECT cash FROM users WHERE id=?", userID)[0]["cash"]
        print("current cash balance: %f" % (currentCash))

        # Format the currency
        cash = locale.currency(currentCash, grouping=True)

        return render_template("deposit.html", cash=cash)


@app.route("/history")
@login_required
def history():
    """Show history of transactions"""

    # Find the user ID of the current user
    userID = session["user_id"]

    # Query all the transactions of the user
    transactionHistory = db.execute("SELECT * FROM transactions WHERE user_id=?", userID)

    #print("User " + str(userID) +"'s transaction history:")

    for transaction in transactionHistory:
        # Replace the "cost" value in the dictionaries with currency-formatted version
        transaction["cost"] = locale.currency(transaction["cost"], grouping=True)

        if transaction["stock_symbol"] == "DEPOSIT":
            transaction["shares_count"] = ""

        # print(transaction)

    return render_template("history.html", transactions=transactionHistory)


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
    if request.method == "POST":

        # Get the symbol from the form
        symbol = request.form.get("symbol")

        # Capitalize all the letters in the symbol
        symbol = symbol.upper()

        # Get information related to symbol
        dictLookup = lookup(symbol)
        # print(dictLookup)

        # Show error page if the symbol doesn't exist
        if not dictLookup:
            errorQuote = "The symbol \"" + symbol + "\" doesn't exist."
            # return render_template("quoted.html", quote=errorQuote)
            return apology(errorQuote)

        # Get the name of the company and stock price
        companyName = dictLookup["name"]
        stockPrice = dictLookup["price"]

        # Format the stock price as currency
        stockPrice = locale.currency(stockPrice, grouping=True)

        return render_template("quoted.html", name=companyName, symbol=symbol, price=stockPrice)

    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    if request.method == "POST":

        # Get the user input from the form
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Search for the username in the users table
        rows = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Check if username has been input
        if username in ["", None]:
            return apology("No username has been entered.")

        # Check if username is not already in the database
        if len(rows) != 0:
            return apology("The username \"" + username + "\" is already in use.")

        # Check if password has been input
        if password in ["", None]:
            return apology("No password has been entered.")

        # Check if confirmation has been input
        if confirmation in ["", None]:
            return apology("The passwords did not match.")

        # Check if password and confirmation match
        if password != confirmation:
            return apology("The passwords do not match.")

        # Hash the user's password
        hashedPassword = generate_password_hash(password)

        # Insert the username and hashed password into the finance.db database
        db.execute("INSERT INTO users(username, hash) VALUES(?, ?)", username, hashedPassword)

        return render_template("login.html")

    else:
        return render_template("register.html")


@app.route("/search", methods=["GET", "POST"])
def search():
    # Get the text after "search?q="
    entry = request.args.get("q")

    # Get API KEY
    api_key = os.environ.get("API_KEY")

    # Get all of the stock symbols
    url = f"https://cloud.iexapis.com/stable/ref-data/iex/symbols?token={api_key}"
    symbols = requests.get(url)  # Type: <class: 'requests.models.Response'>
    # print("\ntype of object: " + str(type(symbols)) + "\n")
    symbols = symbols.json()  # New type: <class 'list'>
    # print("type of object: " + str(type(symbols)) + "\n")

    # Initialize list
    matchedSymbols = []

    # Iterate through all the symbols and add the matching ones to a list
    for symbolInfo in symbols:
        if re.match(entry, symbolInfo["symbol"]) != None:
            matchedSymbols.append(symbolInfo)

    return jsonify(matchedSymbols)


@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":

        # Get the user input from the form
        userID = session["user_id"]
        symbol = request.form.get("symbol")
        amount = request.form.get("shares")

        # Check if the user selected a symbol
        if not symbol:
            return apology("A stock symbol must be selected.")

        # Check if the user entered an amount
        if not amount:
            return apology("An amount must be selected.")

        # Cast the amount to an integer
        try:
            amount = int(amount)
        except ValueError:
            return apology("A valid integer amount of shares must be entered.")

        # Find all the stock types the user has
        stockTypesDict = db.execute("SELECT DISTINCT stock_symbol FROM transactions WHERE user_id=?", userID)

        stockTypesList = []

        # Create a list of the stock types owned by the user
        for stockType in stockTypesDict:
            stockTypesList.append(stockType["stock_symbol"])

        # Double check if the user has a stock of the selected type
        if symbol not in stockTypesList:
            return apology("The user does not own any \"" + symbol + "\" stocks.")

        # Check if the user has input a number greater than 1
        if amount < 1:
            return apology("The shares amount must be 1 or more.")

        # Find the total amount of stocks the user owns of the type selected
        totalStocksOfSelectedType = db.execute("SELECT SUM(shares_count) sum FROM transactions WHERE user_id=? \
                                                AND stock_symbol=?", userID, symbol)[0]["sum"]

        #print("User " + str(userID) + "'s total stocks of type " + symbol + ": " + str(totalStocksOfSelectedType))

        # Check if the user has enough stocks of the type selected
        if amount > totalStocksOfSelectedType:
            return apology("The user does not have enough stocks of type \"" + symbol + ".\"")

        # Get the current time and format it
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Look up the current cost of a share of the type selected
        cost = lookup(symbol)["price"]

        # Insert into the transactions table
        # Make the amount negative as this is a sale
        db.execute("INSERT INTO transactions(user_id, stock_symbol, cost, shares_count, time) VALUES(?, ?, ?, ?, ?)",
                   userID, symbol, cost, (-1 * amount), now)

        # Calculate the total cost/return of the stocks
        totalCost = amount * cost

        # Get the user's cash balance
        cash = db.execute("SELECT cash FROM users WHERE id=?", userID)[0]["cash"]

        # Calculate the user's remaining cash balance
        updatedCash = cash + totalCost

        # Account for errors in floating-point addition
        updatedCash = (int(updatedCash * 100)) / 100

        # print(f"\ncash: {cash}")
        # print(f"total cost: {totalCost}")
        # print(f"balance after sale: {updatedCash}\n")

        # Update the cash balance in the users table
        db.execute("UPDATE users SET cash=? WHERE id=?", updatedCash, userID)

        # Flash the message to be passed to the index page
        flash(f"{amount} {symbol} share(s) sold!")

        return redirect("/")

    else:
        # Store the user's ID
        userID = session["user_id"]

        # Find the types of stocks purchased by the user
        # Keep the stock_symbol 'DEPOSIT' out of the query results
        stockTypes = db.execute("SELECT DISTINCT stock_symbol FROM transactions WHERE user_id=? AND stock_symbol <> 'DEPOSIT'",
                                userID)

        return render_template("sell.html", stockTypes=stockTypes)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)

# Code to launch the local server
if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=8080)