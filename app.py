"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
import os
from flask import Flask, render_template, redirect, url_for, request, current_app
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_wtf import Form, FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import TextField, BooleanField, PasswordField, SubmitField, validators, StringField, TextAreaField, RadioField
from wtforms.validators import InputRequired, Length, EqualTo, Email, ValidationError, DataRequired
from models import User

db = SQLAlchemy()
migrate = Migrate()

app = Flask(__name__)
app.secret_key = 'replace later'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://logyrzrjbnpwxv:268c35e00ea5eb3a14ba3bd1f6a41bd7e11cc98c10a7a2f2b1c9af0c50b95db5@ec2-34-204-121-199.compute-1.amazonaws.com:5432/degvjsokhihl0p'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_BINDS = False
db = SQLAlchemy(app)
app.debug = True
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
csrf = CSRFProtect(app)
csrf = CSRFProtect()

import requests
# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app

def invalid_credentials(form, field):
    """Username and password checker"""
    username_entered = form.username.data
    password_entered = field.password.data

    # Check if credentials is valid
    user_object = User.query.filter_by(username=username_entered).first()
    if user_object is None:
        raise ValidationError("One of the details is incorrect")
       

    elif password_entered != user_object.password:
        raise ValidationError("One of the details is incorrect")


class RegistrationForm(FlaskForm):

    username = StringField('Username', validators=[InputRequired(message="Username required"), Length(min=4, max=20,
                                                                               message="Username between 4 and 25 characters")])
    email = TextField('Email', [validators.Length(min=6, max=50)])
    password = PasswordField('Password', validators=[InputRequired(message="Password required"), Length(min=4, max=20,
                                                                               message="Username between 4 and 25 characters")])
    confirm = PasswordField('Repeat Password', validators=[InputRequired(message="Password required"),
                                                           EqualTo('password', message="Passwords must match")])

    submit_button = SubmitField('Create')

    def validate_username(self, username):
        user_object = User.query.filter_by(username=username.data).first()
        if user_object:
            raise ValidationError("Username already exists, please use a different username")
    
    def validate_email(self, email):
        user_object = User.query.filter_by(email=email.data).first()
        if user_object:
            raise ValidationError("Email already exists, please use a different email")



@app.route("/", methods=['GET', 'POST'])
def index():

    reg_form = RegistrationForm()
    # updates database on successful registration
    if reg_form.validate_on_submit():
        hashed_password = generate_password_hash(reg_form.password.data, method='sha256')
        username = reg_form.username.data
        password = hashed_password
        email = reg_form.email.data

        #adding user to DB
        user = User(username=username, password=password, email=email)
        session.add(user)
        session.commit()            

        return redirect(url_for('login'))
    return render_template('registration.html', form=reg_form)

@login_manager.user_loader
def user_loader(id):
    """Given *user_id*, return the associated Userobject"""
    #the current user is current_user.username remember this later while working with id
    return User.query.get(int(id))

class LoginForm(FlaskForm):
    """Login form"""
    
    username = StringField('username', validators=[InputRequired(message="Username Required")])
    password = PasswordField('password', validators=[InputRequired(message="Password required")])
    submit_button = SubmitField('Login')


@app.route('/signin', methods=['GET', 'POST'])
def login():
    # to prevent a logged in user from logging in again:
    if current_user.is_authenticated:
        return redirect(url_for('search_page'))
    form = LoginForm()
    
    # Allow login if validation success
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user)
                return redirect(url_for('search_page')) #we will redirect to search
        flash('Invalid credentials')
        return redirect(url_for('login'))

    return render_template('login.html', form=form)


@app.route('/logout', methods=["GET", "POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/search', methods=['GET', 'POST'])
def search_page():
        
    return render_template("search.html")





@app.route('/')
def dashboard():
    """Renders a sample page."""
    return render_template("dashboard.html")

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
