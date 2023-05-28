from flask import Flask, render_template, redirect, request, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager, login_user, login_required, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from flask_bootstrap import Bootstrap

# app and app's configs
app = Flask(__name__)
app.config["SECRET_KEY"] = "@0thisisaSECRET_KEY0@"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///blog.db"
Bootstrap(app)

# Login
login_manager = LoginManager()
login_manager.init_app(app)

# db creation
db = SQLAlchemy()
db.init_app(app)


# db models
class User(UserMixin, db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.Text, unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)
    expenses = db.relationship("Expense", back_populates="user")


class Expense(db.Model):
    __tablename__ = "expenses"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False)
    type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    user = db.relationship("User", back_populates="expenses")


with app.app_context():
    db.create_all()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


@app.route("/", methods=['GET', 'POST'])
def home():
    if request.method == "POST":
        form_action = str(request.form['formAction'])
        print(form_action)
        email = request.form.get('email')
        user = User.query.filter_by(email=email).first()
        print(user)
        if form_action == 'login':
            if user is None:
                flash("Invalid email, try again.", 'error')
                print("yea")
            else:
                print("oo")
                password = request.form.get('password')
                if check_password_hash(user.password, password):
                    login_user(user)
                    username = user.username
                    return redirect(url_for("dashboard", user=username))
                else:
                    print("no")
                    flash("Incorrect Password", 'error')
        else:
            if user:
                flash("User already exists, try logging in." 'error')
            username = request.form.get('username')
            password = generate_password_hash(request.form.get('password'), method="pbkdf2:sha256", salt_length=8)
            user_data = User(
                username=username,
                email=email,
                password=password
            )
            db.session.add(user_data)
            db.session.commit()
            login_user(user_data)
            return redirect(url_for("dashboard", user=username))
    return render_template("home.html")


@app.route('/dashboard/<user>')
@login_required
def dashboard(user):
    return render_template('dashboard.html', user=user)


@app.route('/about')
def about():
    return render_template('about-us.html')


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route('/api/transactions', methods=['POST'])
def add_transaction():
    data = request.get_json()

    # Extract the relevant data from the JSON payload
    name = data['name']
    amount = data['amount']
    date = data['date']
    transaction_type = data['type']

    # Create a new Expense instance
    expense = Expense(
        name=name,
        amount=amount,
        date=date,
        type=transaction_type
    )

    # Fetch the user from the database (you may need to adjust this based on your authentication setup)
    user = User.query.filter_by(username='your_username').first()
    if user is None:
        return jsonify({'message': 'User not found'}), 404

    # Associate the expense with the user
    expense.user = user

    # Add the expense to the session and commit to the database
    db.session.add(expense)
    db.session.commit()

    return redirect(url_for('manage'))


if __name__ == "__main__":
    app.run(debug=True)

# To credit where credit is due
# For The Expense Manager
# Author: refinedguides; URL: https://github.com/refinedguides/expense-tracker-js
