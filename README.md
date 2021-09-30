# Stocks Application for Investing

This project was completed as to fulfill the requirements of [problem set 9](https://cs50.harvard.edu/x/2021/psets/9/finance) of [CS50 Introduction to Programming](https://online-learning.harvard.edu/course/cs50-introduction-computer-science?delta=0). A live version of the application can be found on [Replit](https://replit.com/@john-albright/stocks-application-cs50-finance). The project was built using the framework Flask and therefore, utilizes Python for the back end operations and Jinja to allow templates for the front end. A SQL database titled finance.db is used to store user information and transactions. As an extension of the assignment, the deposit feature was added in addition to an AJAX call on the quote.html page to generate a list of all stock acronyms available while the user types. 

The [Python CS50 library](https://github.com/cs50/python-cs50/tree/main/src/cs50) is essential to the functioning of the code in application.py, especially commands concerning the SQL database. The [IEX API](https://iexcloud.io/) is used to access the current prices of all stocks available. 

To begin to use this application, set up a [virtual envrionment](https://virtualenv.pypa.io/en/stable/). To install `virtualenv` on your local machine, use pip: 
```
pip install virutalenv
```

Then, set up the virtual environment by typing a statement similar to the following:
```
virtualenv -p python3.9 flask-env
```
The version of python may have another name on your machine; `python` and `python3` may also work. Format strings are used in the python code of the application, so python 3.6+ must be used to run the code. The `flask-env` portion of the code is simply the directory where the virtual envrionment will be created.

Enter the the directory and activate the virtual environment.
```
cd flask-env
source bin/activate
```

Install the dependendies using the requirements.txt file provided. You will have to use a relative (which depends on where the flask-env directory is) or the absolute path of the requirements.txt file. In the code below, the virtual environment is within this GitHub repository.
```
pip install -r ../requirements.txt
```

After all the dependencies are installed, run the application.py file. Again, the 
```
python ../application.py
```

The application will raise an error if the API_KEY obtained from [IEX](https://iexcloud.io/) has not been specificied in a .env file within the GitHub repository folder. The [live Replit version](https://replit.com/@john-albright/stocks-application-cs50-finance) of this application includes my API as a secret variable.  

The application will be located at port 8080 on your local host, that is, it can be accessed by going to any browser on the local machine and entering localhost:8080 in the search bar.

Finally, deactivate the virtual environment when you are finished.
```
deactivate
```

To see two users' profiles, log in with:
- username: john, password: john
- username: danny, password: danny