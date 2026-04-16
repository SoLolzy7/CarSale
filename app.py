import os
from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
import stripe
from functools import wraps

# ================== INIT ==================
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")

# ===== DATABASE (PostgreSQL) =====
db_url = os.getenv("DATABASE_URL")

if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ===== STRIPE =====
stripe.api_key = os.getenv("STRIPE_SECRET_KEY")

# ===== LOGIN =====
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# ================== MODELS ==================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200))
    price = db.Column(db.Integer)
    description = db.Column(db.Text)
    image_url = db.Column(db.String(500))

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'))
    amount = db.Column(db.Integer)

# ================== CREATE TABLE ==================
with app.app_context():
    db.create_all()

# ================== LOGIN ==================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# ================== ADMIN ==================

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            flash("Admin only")
            return redirect(url_for("index"))
        return f(*args, **kwargs)
    return decorated

# ================== ROUTES ==================

@app.route('/')
def index():
    cars = Car.query.all()
    return render_template('index.html', cars=cars)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = User(
            username=request.form['username'],
            password=request.form['password'],
            email=request.form['email']
        )
        db.session.add(user)
        db.session.commit()
        flash("Registered!")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user = User.query.filter_by(
            username=request.form['username'],
            password=request.form['password']
        ).first()

        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash("Wrong credentials")

    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/add_car', methods=['GET', 'POST'])
@login_required
@admin_required
def add_car():
    if request.method == 'POST':
        car = Car(
            name=request.form['name'],
            price=int(float(request.form['price']) * 100),
            description=request.form['description'],
            image_url=request.form['image_url']
        )
        db.session.add(car)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_car.html')

@app.route('/buy/<int:car_id>')
@login_required
def buy_car(car_id):
    car = Car.query.get(car_id)

    session['car_id'] = car.id
    session['amount'] = car.price

    checkout_session = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=[{
            'price_data': {
                'currency': 'usd',
                'product_data': {'name': car.name},
                'unit_amount': car.price,
            },
            'quantity': 1,
        }],
        mode='payment',
        success_url=url_for('payment_success', _external=True),
        cancel_url=url_for('index', _external=True),
    )

    return redirect(checkout_session.url)

@app.route('/payment_success')
@login_required
def payment_success():
    order = Order(
        user_id=current_user.id,
        car_id=session.get('car_id'),
        amount=session.get('amount')
    )
    db.session.add(order)
    db.session.commit()

    return render_template('payment_success.html')

@app.route('/my_orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).all()
    return render_template('my_orders.html', orders=orders)

# ================== RUN ==================

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)