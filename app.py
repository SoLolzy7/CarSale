import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import stripe
from functools import wraps

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'super-secret-key-change-in-production'  # Change this in production!

# Database configuration
DATABASE = 'car_shop.db'

app.config['STRIPE_PUBLISHABLE_KEY'] = os.getenv("STRIPE_PUBLISHABLE_KEY")
app.config['STRIPE_SECRET_KEY'] = os.getenv("STRIPE_SECRET_KEY")
stripe.api_key = app.config['STRIPE_SECRET_KEY']

# Flask-Login setup
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to purchase cars.'

# Database helper functions
def get_db():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    return db

def init_db():
    """Create database tables if they don't exist"""
    db = get_db()
    cursor = db.cursor()
    
    # Create User table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            is_admin INTEGER DEFAULT 0
        )
    ''')
    
    # Create Car table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS car (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            price INTEGER NOT NULL,
            description TEXT,
            image_url TEXT
        )
    ''')
    
    # Create Order table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS "order" (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            car_id INTEGER NOT NULL,
            stripe_payment_id TEXT,
            purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            amount INTEGER,
            FOREIGN KEY (user_id) REFERENCES user (id),
            FOREIGN KEY (car_id) REFERENCES car (id)
        )
    ''')
    
    db.commit()
    db.close()
    print("Database initialized successfully!")

# Initialize database when app starts
init_db()

# User class for Flask-Login
class User(UserMixin):
    def __init__(self, id, username, email, is_admin):
        self.id = id
        self.username = username
        self.email = email
        self.is_admin = is_admin

@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    user = db.execute('SELECT * FROM user WHERE id = ?', (user_id,)).fetchone()
    db.close()
    if user:
        return User(user['id'], user['username'], user['email'], user['is_admin'])
    return None

# Admin decorator
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash('Admin access required.')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Routes
@app.route('/')
def index():
    """Home page - display all available cars"""
    db = get_db()
    cars = db.execute('SELECT * FROM car').fetchall()
    db.close()
    return render_template('index.html', cars=cars)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']  # In production, hash this password!
        email = request.form['email']
        
        db = get_db()
        try:
            db.execute('INSERT INTO user (username, password, email) VALUES (?, ?, ?)',
                      (username, password, email))
            db.commit()
            flash('Registration successful! Please log in.')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Username or email already exists.')
        finally:
            db.close()
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        db = get_db()
        user = db.execute('SELECT * FROM user WHERE username = ? AND password = ?',
                         (username, password)).fetchone()
        db.close()
        
        if user:
            user_obj = User(user['id'], user['username'], user['email'], user['is_admin'])
            login_user(user_obj)
            flash('Logged in successfully!')
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password.')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    """Logout user"""
    logout_user()
    flash('You have been logged out.')
    return redirect(url_for('index'))

@app.route('/add_car', methods=['GET', 'POST'])
@login_required
@admin_required
def add_car():
    """Admin page to add new cars"""
    if request.method == 'POST':
        name = request.form['name']
        price = int(float(request.form['price']) * 100)  # Convert to cents for Stripe
        description = request.form['description']
        image_url = request.form['image_url']
        
        db = get_db()
        db.execute('INSERT INTO car (name, price, description, image_url) VALUES (?, ?, ?, ?)',
                  (name, price, description, image_url))
        db.commit()
        db.close()
        
        flash('Car added successfully!')
        return redirect(url_for('index'))
    
    return render_template('add_car.html')

@app.route('/buy/<int:car_id>')
@login_required
def buy_car(car_id):
    """Create Stripe checkout session"""
    db = get_db()
    car = db.execute('SELECT * FROM car WHERE id = ?', (car_id,)).fetchone()
    db.close()
    
    if not car:
        flash('Car not found.')
        return redirect(url_for('index'))
    
    # Store car ID in session for success page
    session['pending_car_id'] = car['id']
    session['pending_amount'] = car['price']
    
    # Create Stripe checkout session
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': car['name'],
                        'description': car['description'],
                    },
                    'unit_amount': car['price'],
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url=url_for('payment_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=url_for('index', _external=True),
        )
        
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        flash('Payment processing error. Please try again.')
        return redirect(url_for('index'))

@app.route('/payment_success')
@login_required
def payment_success():
    """Handle successful payment"""
    car_id = session.pop('pending_car_id', None)
    amount = session.pop('pending_amount', None)
    
    if not car_id:
        flash('No pending purchase found.')
        return redirect(url_for('index'))
    
    # Create order record
    db = get_db()
    db.execute('INSERT INTO "order" (user_id, car_id, amount) VALUES (?, ?, ?)',
              (current_user.id, car_id, amount))
    db.commit()
    db.close()
    
    flash('Purchase successful! Thank you for your order.')
    return render_template('payment_success.html')

@app.route('/my_orders')
@login_required
def my_orders():
    """Display user's purchase history"""
    db = get_db()
    orders = db.execute('''
        SELECT o.*, c.name as car_name, c.image_url 
        FROM "order" o 
        JOIN car c ON o.car_id = c.id 
        WHERE o.user_id = ?
        ORDER BY o.purchase_date DESC
    ''', (current_user.id,)).fetchall()
    db.close()
    
    return render_template('my_orders.html', orders=orders)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
