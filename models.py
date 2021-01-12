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

    role_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user_wallet = relationship('Wallets', backref='wallet', lazy='dynamic')

class Roles(UserMixin, db.Model):
    __tablename__ = "roles"
    id = db.Column(db.Integer, primary_key=True)
    roles = db.column(db.String(25))
    
    user_role = relationship('RolePrivileges', backref='role_privilege', lazy='dynamic')
   

class Wallets(UserMixin, db.Model):
     __tablename__ = "wallets"
     id = db.Column(db.Integer, primary_key=True)
     currency = db.Column(db.float)

     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

class Privileges(UserMixin, db.Model):
    __tablename__ = "privileges"
    id = db.Column(db.Integer, primary_key=True)
    user_privileges = db.column(db.String)

    role_privilege = relationship('RolePrivileges', backref='roles', lazy='dynamic')

class RolePrivileges(UserMixin, db.Model):
     __tablename__ = "rolefunctions"
     id = db.Column(db.Integer, primary_key=True)
     role_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
     privilege_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
