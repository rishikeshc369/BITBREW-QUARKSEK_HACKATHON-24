from flask import Flask, render_template, request
import sqlite3
app = Flask(__name__)

# Connect to SQLite database
conn = sqlite3.connect('mydatabase.db')
c = conn.cursor()

# Create users table if not exists
c.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER
             )''')
conn.commit()
@app.route('/')
def index():
    return render_template('index.html')

from flask import Flask, render_template, request, redirect, url_for
import sqlite3

app = Flask(__name__)

# Function to establish a connection to the SQLite database
def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Function to create the users table if it doesn't exist
def create_users_table():
    conn = get_db_connection()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    phone TEXT NOT NULL,
                    password TEXT NOT NULL
                 )''')
    conn.commit()
    conn.close()

# Create users table
create_users_table()

# Route to render the index.html template
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle sign-up form submission
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        password = request.form['password']
        
        # Connect to the database
        conn = get_db_connection()
        c = conn.cursor()

        # Insert the new user into the database
        c.execute('''INSERT INTO users (name, email, phone, password) VALUES (?, ?, ?, ?)''', (name, email, phone, password))
        conn.commit()
        conn.close()

        # Redirect to the dashboard after successful sign-up
        return redirect(url_for('dashboard'))

# Route to handle login form submission
@app.route('/signin', methods=['POST'])
def signin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Connect to the database
        conn = get_db_connection()
        c = conn.cursor()

        # Query the database to check if the user exists and the password is correct
        c.execute('''SELECT * FROM users WHERE email = ? AND password = ?''', (email, password))
        user = c.fetchone()

        if user:
            # User authenticated, redirect to the dashboard
            conn.close()
            return redirect(url_for('dashboard'))
        else:
            # Authentication failed, redirect back to the index page with an error message
            error_message = "Invalid email or password. Please try again."
            conn.close()
            return render_template('index.html', error_message=error_message)

# Route to render the dashboard page
@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == '__main__':
    app.run(debug=True)
