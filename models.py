from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_sqlalchemy import Model
from flask_login import LoginManager, UserMixin
from sqlalchemy.orm import relationship
from flask_marshmallow import Marshmallow
app =  Flask(__name__)
db = SQLAlchemy(app)
ma = Marshmallow(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
     
class User(UserMixin, db.Model):
    """User model"""

    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(250), unique=True, nullable=False)
    email = db.Column(db.String(250), unique=True, nullable=False)
    password = db.Column(db.String(250), nullable=False)
    

    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'), nullable=False)


    user_wallet = relationship('Wallets', backref='wallet', lazy='dynamic')

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username', 'password', 'email', 'role_id')
#init schema
user_schema = UserSchema()
users_schema = UserSchema(many=True)

class Roles(UserMixin, db.Model):

    __tablename__ = "roles"

    id = db.Column(db.Integer, primary_key=True)
    roles = db.Column(db.String(25))
    
class Currencies(UserMixin, db.Model):
    __tablename__ = "currency"
    id = db.Column(db.Integer, primary_key=True)
    currency = db.Column(db.String(25))
    code = db.Column(db.Integer)

    wallet_currency = relationship('Wallets', backref='wallet_currency', lazy='dynamic')

class CurrencySchema(ma.Schema):
    class Meta:
        fields = ('id', 'currency', 'code')
#init schema
currency_schema = CurrencySchema()
currencies_schema = CurrencySchema(many=True)


class Wallets(UserMixin, db.Model):

     __tablename__ = "wallets"

     id = db.Column(db.Integer, primary_key=True)
     balance = db.Column(db.Float, default=0.00)

     user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
     currency_id = db.Column(db.Integer, db.ForeignKey('currency.id'), nullable=False)

     pending_wallet = relationship('PendingApproval', backref='pending_wallet', lazy='dynamic')

class WalletSchema(ma.Schema):
    class Meta:
        fields = ('id', 'balance', 'user_id', 'currency_id')
#init schema
wallet_schema = WalletSchema()
wallets_schema = WalletSchema(many=True)

class PendingApproval(UserMixin, db.Model):
    __tablename__ = "pendingapproval"
    id = id = db.Column(db.Integer, primary_key=True)
    pending_balance = db.Column(db.Float)
    approved = db.Column(db.Boolean, default=False)
    wallet_id = db.Column(db.Integer, db.ForeignKey('wallets.id'), nullable=False)