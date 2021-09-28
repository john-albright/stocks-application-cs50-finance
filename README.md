# Stocks Application for Investing

This project was completed as to fulfill the requirements of [problem set 9](https://cs50.harvard.edu/x/2021/psets/9/finance) of [CS50 Introduction to Programming](https://online-learning.harvard.edu/course/cs50-introduction-computer-science?delta=0). A live version of the application can be found on [Replit](https://replit.com/@john-albright/stocks-application-cs50-finance). The project was built using the framework Flask and therefore, utilizes Python for the back end operations and Jinja to allow templates for the front end. A SQL database titled finance.db is used to store user information and transactions. As an extension of the assignment, the deposit feature was added in addition to an AJAX call on the quote.html page to generate a list of all stock acronyms available while the user types. 

The [Python CS50 library](https://github.com/cs50/python-cs50/tree/main/src/cs50) is essential to the functioning of the code in application.py, especially commands concerning the SQL database. 

To see two users' profiles, log in with:
- username: john, password: john
- username: danny, password: danny