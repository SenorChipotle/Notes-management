from crypt import methods
from unicodedata import category
from flask import Flask,render_template,request,session,redirect,url_for,session
import mysql.connector
from flask_mysqldb import MySQL
import yaml 
import MySQLdb.cursors
import re

app=Flask(__name__)
app.secret_key = 'key'

db = yaml.full_load(open('db.yaml'))
app.config['MYSQL_HOST'] = db['mysql_host']
app.config['MYSQL_USER'] = db['mysql_user']
app.config['MYSQL_PASSWORD'] = db['mysql_password']
app.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(app)

@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
    # Check if form exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE user_name = %s AND password = %s', (username, password,))
        # Fetch one record and return result
        account = cursor.fetchone()
        if account:
            # Create session data, we can access this data in other routes
            session['loggedin'] = True
            session['id'] = account['id']
            session['username'] = account['username']
            # Redirect to home page
            # return 'Logged in successfully!'
            return redirect(url_for('home.html'))

        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'

    msg = ''
    return render_template('login.html')

@app.route('/home' , methods = ['GET','POST'])
def create():
    if request.method == 'POST':    
        note = request.form['note']
        cur = mysql.connection.cursor()
        cur.execute("INSERT into notes(notes) values (%s)",(note,))
        mysql.connection.commit()
        cur.close()
        return "note succesfully created"
    return render_template('home.html')

def fetch():
    if request.method == 'POST' and 'category' in request.form:
        cur = mysql.connection.cursor 
        cat_name = request.form['category']
        cur.execute('''SELECT * from note where category_name = (%s) ''' , (cat_name,))
        note = cur.fetchone()

        return ("note is = ",note)

    elif request.method == 'POST' and 'category' not in request.form:
        return "please select a category"

@app.route('/register',methods = ['GET','POST'])
def register():
    msg = ''
    # Check if "username", "password" and "email" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form and 'email' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']

        # Check if account exists using MySQL
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM users WHERE user_name = %s', (username,))
        account = cursor.fetchone()
        # If account exists show error and validation checks
        if account:
            msg = 'Account already exists!'
        elif not re.match(r'[^@]+@[^@]+\.[^@]+', email):
            msg = 'Invalid email address!'
        elif not re.match(r'[A-Za-z0-9]+', username):
            msg = 'Username must contain only characters and numbers!'
        elif not username or not password or not email:
            msg = 'Please fill out the form!'
        else:
            # Account doesnt exists and the form data is valid, now insert new account into accounts table
            cursor.execute('INSERT INTO users (`username`, `password`, `email`) VALUES (%s, %s, %s)', (username, password, email,))
            mysql.connection.commit()
            msg = 'You have successfully registered!'
    elif request.method == 'POST':
        # Form is empty... (no POST data)
        msg = 'Please fill out the form!'
    # Show registration form with message (if any)
    return render_template('register.html')
    
if __name__== "__main__":
    app.run(debug=True)

