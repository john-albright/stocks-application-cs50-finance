import os
import requests
import urllib.parse

from flask import redirect, render_template, request, session
from functools import wraps


def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.

        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return render_template("apology.html", top=code, bottom=escape(message)), code


def login_required(f):
    """
    Decorate routes to require login.

    https://flask.palletsprojects.com/en/1.1.x/patterns/viewdecorators/
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated_function


def lookup(symbol):
    """Look up quote for symbol."""

    # Contact API
    try:
        api_key = os.environ.get("API_KEY")
        url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(symbol)}/quote?token={api_key}"
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException:
        return None

    # Parse response
    try:
        quote = response.json()
        return {
            "name": quote["companyName"],
            "price": float(quote["latestPrice"]),
            "symbol": quote["symbol"]
        }
    except (KeyError, TypeError, ValueError):
        return None


"""
This function takes too long to implement.
The API offers an easier way to get all the symbols.

def generateFullList():
    # Declare list with all the letters of the alphabet
    alphabet = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X', 'Y', 'Z']

    # Initialize list of all combinations with the alphabet values alone
    combinations = alphabet.copy()

    # Find all combinations of letters of the alphabet
    for letter1 in alphabet:
        for letter2 in alphabet:
            newCombo = letter1 + letter2
            combinations.append(newCombo)
            for letter3 in alphabet:
                newCombo = letter1 + letter2 + letter3
                combinations.append(newCombo)
                for letter4 in alphabet:
                    newCombo = letter1 + letter2 + letter3 + letter4
                    combinations.append(newCombo)

    print(len(combinations)) # 475,254 -- should be 26^4 = 456976
    # Initialize list to be populated with information on stocks
    fullList = []

    for combination in combinations:
        # Check the website with all combinations
        try:
            api_key = os.environ.get("API_KEY")
            url = f"https://cloud.iexapis.com/stable/stock/{urllib.parse.quote_plus(combination)}/quote?token={api_key}"
            response = requests.get(url)
            response.raise_for_status()
            quote = response.json()

            # Add the valid symbols to the list
            if quote["latestPrice"] not in ["", None] and quote["companyName"] not in ["", None]:
                fullList.append({
                    "symbol": quote["symbol"]
                })
        except requests.RequestException:
            continue
        except (TypeError, KeyError):
            continue

    return fullList
"""


def usd(value):
    """Format value as USD."""
    return f"${value:,.2f}"
