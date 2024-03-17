from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import validators
import pika
import subprocess
import zapin
from urllib.parse import urlparse

app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Initialize RabbitMQ connection and channel
connection = None
channel = None

def connect_to_rabbitmq():
    global connection, channel
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='url_queue')
    except pika.exceptions.AMQPError as e:
        print("Error connecting to RabbitMQ:", e)

connect_to_rabbitmq()  # Establish RabbitMQ connection on application start
                                                                                            
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    urls = db.relationship('Url', backref='user', lazy=True)

class Url(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url = db.Column(db.String(200), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_password = generate_password_hash(password)

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):
            session['logged_in'] = True
            session['user_id'] = user.id  # Store the user ID in the session
            return redirect(url_for('urlcollector'))
        else:
            return 'Invalid username or password'

    return render_template('login.html')

@app.route('/urlcollector', methods=['GET', 'POST'])
def urlcollector():
    if request.method == 'POST':
        target = request.form.get('url')
        if target:
            domain = separate_http_https_domain(target)
            output = run_nmap_scan(domain)  
            
            # Run Nmap scan
            # You can process the output or display it as needed
            zap_path=r"C:\Program Files\ZAP\Zed Attack Proxy\zap-2.14.0.jar"
            zap_port = 9090
            zapin.start_zap(zap_path, zap_port)
            zap_proxy='http://localhost:9090'
            api_key='vc83kmprrkkg7g2is47ghfa6v1'
            zapin.scan_with_zap(target, zap_proxy, api_key)
            
            try:
                with open('scan_results.txt', 'w') as file:
                    file.write(output)
                return "Scan files saved Successfully"
            except Exception as e:
                return f"Error saving scan results to file: {e}"

        else:
            return "No target provided for scanning."

    return render_template('urlcollector.html')

def separate_http_https_domain(url):
    parsed_url = urlparse(url)
    if parsed_url.scheme in ['http', 'https']:
        netloc = parsed_url.netloc
        if netloc.startswith('www.'):
            return netloc[len('www.'):]
        else:
            return netloc
    else:
        return None
        
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('user_id', None)  # Clear the user ID from the session
    return redirect(url_for('home'))

def run_nmap_scan(target):
    try:
        # Run Nmap scan and capture output
        result = subprocess.run(['nmap', '-Pn', target], capture_output=True, text=True, timeout=300)
        return result.stdout
    except subprocess.TimeoutExpired:
        return "Scan took too long to complete."
    except Exception as e:
        return f"Error executing Nmap command: {e}"

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
        except Exception as e:
            print("Error creating database tables:", e)
    app.run(debug=True)
