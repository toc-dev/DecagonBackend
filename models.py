from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import Model
from flask_login import LoginManager, UserMixin
from sqlalchemy.orm import relationship

app =  Flask(__name__)
db = SQLAlchemy(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
     
class User(UserMixin, db.Model):
    """User model"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), unique=True, nullable=False)

class Roles(UserMixin, db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    admin = db.column(db.String(25))
    elite = db.column(db.String(25))
    noob = db.column(db.String(25))

class Wallets(UserMixin, db.Model):
     __tablename__ = "wallets"
     id = db.Column(db.Integer, primary_key=True)
     USD = db.Column(db.float)
     GBP = db.Column(db.float)
     EUR = db.Column(db.float)
     JPY = db.Column(db.float)

class Functions(UserMixin, db.Model):
    __tablename__ = "functions"
    id = db.Column(db.Integer, primary_key=True)
    user_functions = db.column(db.String)

class UserRoleFunction(UserMixin, db.Model):
     __tablename__ = "rolefunctions"
     id = db.Column(db.Integer, primary_key=True)
