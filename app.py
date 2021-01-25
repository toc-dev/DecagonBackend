"""
This script runs the application using a development server.
It contains the definition of routes and views for the application.
"""
import os
import datetime
from flask import Flask, request, jsonify, make_response
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.sql import text
from sqlalchemy.orm import scoped_session, sessionmaker
from flask_migrate import Migrate
from flask_bootstrap import Bootstrap
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
import uuid
from models import User, UserSchema, Wallets, WalletSchema, Currencies, CurrencySchema, PendingApproval
from werkzeug.security import generate_password_hash, check_password_hash
from flask_restful import Resource
from flask_script import Manager
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
#db = SQLAlchemy()

user_schema = UserSchema()
users_schema = UserSchema(many=True)
currency_schema = CurrencySchema()
currencies_schema = CurrencySchema(many=True)
wallet_schema = WalletSchema()
wallets_schema = WalletSchema(many=True)

app = Flask(__name__)
app.secret_key = 'replace later'

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres://logyrzrjbnpwxv:268c35e00ea5eb3a14ba3bd1f6a41bd7e11cc98c10a7a2f2b1c9af0c50b95db5@ec2-34-204-121-199.compute-1.amazonaws.com:5432/degvjsokhihl0p'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SQLALCHEMY_BINDS = False
JWT_SECRET_KEY = 'includelater'

jwt = JWTManager(app)
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")
db = SQLAlchemy(app)

app.debug = True
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

engine = create_engine("postgres://logyrzrjbnpwxv:268c35e00ea5eb3a14ba3bd1f6a41bd7e11cc98c10a7a2f2b1c9af0c50b95db5@ec2-34-204-121-199.compute-1.amazonaws.com:5432/degvjsokhihl0p")
Session = scoped_session(sessionmaker(bind=engine))
session = Session()
#manager = Manager(app)
import requests
# Make the WSGI interface available at the top level so wfastcgi can get it.
wsgi_app = app.wsgi_app
migrate = Migrate(app, db)



@app.route("/", methods=['POST'])
def index():
    username = request.json['username']
    email = request.json['email']
    password = generate_password_hash(request.json['password'])
    role_id = request.json['role_id']

    user = User(username=username, password=password, email=email, role_id=role_id)
    session.add(user)
    session.commit() 
    return user_schema.jsonify(user)

  

@app.route("/", methods=['GET'])
def all_users():
    all_users = User.query.all()
    result = users_schema.dump(all_users)
    return users_schema.jsonify(result)

@app.route("/<id>", methods=['GET'])
def one_user(id):
    user = User.query.get(id)
    return user_schema.jsonify(user)

@login_manager.user_loader
def user_loader(user_id):
    """Given *user_id*, return the associated Userobject"""
    #the current user is current_user.username remember this later while working with id
    return User.query.get(int(user_id))


from flask import request
@app.route('/login', methods=['POST'])
def login():
    body = request.get_json()
    username = request.json['username']
    password = request.json['password']

    user = User.query.filter_by(username=username).first()
    #authorized = user.check_password(password)
    
    # to prevent a logged in user from logging in again:
    #if current_user.is_authenticated:
    #    return {'token': access_token}, 200
    
    # Allow login if validation success
   

     #email=body.get('email'), role_id=body.get('role_id'))
    #user = User.query.filter_by(username=body.username.data).first()
    #authorized = check_password_hash(user.password, body.get('password'))
    if not user:
        return jsonify({'error': 'Username or password invalid1'})
    if check_password_hash(user.password, password):
        expires = datetime.timedelta(days=7)
        access_token = create_access_token(identity=str(user.id), expires_delta=expires)
        return {'token': access_token}, 200
    return jsonify({'error': 'Username or password invalid'})

@app.route('/logout', methods=["GET", "POST"])
@jwt_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route("/update", methods=['POST'])
@jwt_required
def update_user():
    body = request.get_json()
    logged_in_id = get_jwt_identity()

    

    username = request.json['username']
    password = request.json['password']
    email = request.json['email']
    role_id = request.json['role_id']

    user = User.query.filter_by(username=username).first()
    user_id = current_user.get_id()
    print(user_id)
    curr_user = User.query.get(logged_in_id)

    if curr_user.role_id == 1:
        print(curr_user.role_id)
        user.username = username
        #user.password = password
        user.email = email
        user.role_id = role_id
        db.session.merge(user)
        db.session.commit()
        return user_schema.jsonify(user)
    if curr_user.id == user.id:
        user.username = username
        #user.password = password
        user.email = email
        user.role_id = user.role_id
        db.session.merge(user)
        db.session.commit()
        return user_schema.jsonify(user)
    return {"error" : "you do not have the facilities for that, big man"}

    db.session.commit()
    print(user_id)
    return user_schema.jsonify(user)

@app.route("/choosecurrency", methods=["POST"])
@jwt_required
def choose_currency():
    user_currency = request.json['currency']
    username = request.json['username']

    user = User.query.filter_by(username=username).first()
    currency = Currencies.query.filter_by(currency=user_currency).first()
    wallet = Wallets.query.filter_by(user_id=user.id).filter_by(currency_id=currency.id).first()
    
    logged_in_id = get_jwt_identity()
    curr_user = User.query.get(logged_in_id)
    wallets = Wallets.query.all()
    print(curr_user.role_id)
    #query wallet
    #if curr_user's role_id is 3, and their user_id already has a currency_id
    #throw error
    #else: attach a currency for the wallet
    if curr_user.id != user.id:
        if curr_user.role_id == 1:
            if user.role_id == 3:
                if user.id in [w.user_id for w in wallets]:
                    return jsonify({"error" : "you cannot perform this action"})
            if user.role_id == 2:
                if wallet is not None:
                    return jsonify({"error" : "you have already registered this currency"})

            wallet = Wallets(user_id=user.id, currency_id=currency.id, balance=0.00)
            db.session.add(wallet)
            db.session.commit()
            return wallet_schema.jsonify(wallet)
    if curr_user.id == user.id:
        if curr_user.role_id == 3:
            if curr_user.id in [w.user_id for w in wallets]:
            #if wallet.currency_id is not None:
                return jsonify({"error" : "you cannot perform this action"})
        if curr_user.role_id == 2:
            if wallet is not None:
                    return jsonify({"error" : "you have already registered this currency"})
        if curr_user.role_id == 1:
            return jsonify({"error": "admin cannot own wallet"})
        wallet = Wallets(user_id=user.id, currency_id=currency.id)
        db.session.add(wallet)
        db.session.commit()
        return wallet_schema.jsonify(wallet)
    return jsonify({"error" : "you are not authorized to perform this action"})
    

@app.route("/changecurrency", methods=['PATCH'])
@jwt_required
def change_currency():
    pass

@app.route("/fundwallet", methods=['POST'])
@jwt_required
def fundWallet():
    #try:
    username = request.json['username']
    amount = request.json['amount']
    currency = request.json['currency']
    wallet_currency = request.json['wallet_currency']

    logged_in_id = get_jwt_identity()
    curr_user = User.query.get(logged_in_id)
    this_wallet_user = User.query.filter_by(username=username).first()
    currency_in = Currencies.query.filter_by(currency=wallet_currency).first()
    wallet_user = Wallets.query.filter_by(user_id=this_wallet_user.id).first()
    

    wallet = Wallets.query.filter_by(user_id=this_wallet_user.id).filter_by(currency_id=currency_in.id).first()       
    print(wallet)
    print(wallet.id)
    if wallet is None:
        if curr_user.id != this_wallet_user.id:
            if curr_user.role_id == 1:
                if this_wallet_user.role_id == 2:
                    wallet = Wallets(user_id=this_wallet_user.id, currency_id=currency_in.id)
                    db.session.add(wallet)
                    db.session.commit()
        if curr_user.id == this_wallet_user.id:
            if curr_user.role_id == 2:
                wallet = Wallets(user_id=this_wallet_user.id, currency_id=currency_in.id)
                db.session.add(wallet)
                db.session.commit()
    
    currency_id = Currencies.query.get(wallet.currency_id)
    this_wallet_user_currency = currency_id.currency

    res = requests.get("https://data.fixer.io/api/convert", params={"access_key": "13af8fb312ee8e46fd999e4dd6538798", "from":currency, "to":this_wallet_user_currency, "amount":amount})
    if res.status_code == 200:
        data = res.json()
        
        amount_in = data['result']
        rounded_amount = round(amount_in, 2)
        
    if curr_user.id != this_wallet_user.id:
        if curr_user.role_id == 1:
            wallet.balance += rounded_amount
            db.session.merge(wallet)
            db.session.commit()
            return wallet_schema.jsonify(wallet)
        return {"error" : "you do not have the facilities to perfrom this action"}

    if curr_user.id == this_wallet_user.id:
        if this_wallet_user.role_id == 3:
            pending_approval = PendingApproval(pending_balance=rounded_amount, wallet_id=wallet.id)
            db.session.add(pending_approval)
            db.session.commit()
            return {"status": "pending_approval"}
        wallet.balance += rounded_amount
        db.session.merge(wallet)
        db.session.commit()

        return wallet_schema.jsonify(wallet)
    
    return {"error": "this wallet is not available to you"}
    #except:
    #    return {"error": "kindly cross-check your inputs"}

@app.route("/withdraw", methods=['POST'])
@jwt_required
def withdraw():
    try:
        username = request.json['username']
        amount = request.json['amount']
        currency = request.json['currency']
        wallet_currency = request.json['wallet_currency']

        currency_id = Currencies.query.filter_by(currency=wallet_currency).first()
        this_wallet_user = User.query.filter_by(username=username).first()
        wallet = Wallets.query.filter_by(user_id=this_wallet_user.id).filter_by(currency_id=currency_id.id).first()
        logged_in_id = get_jwt_identity()
        curr_user = User.query.get(logged_in_id)
        currency_id = Currencies.query.get(wallet.currency_id)
        this_wallet_user_currency = currency_id.currency

        res = requests.get("https://data.fixer.io/api/convert", params={"access_key": "13af8fb312ee8e46fd999e4dd6538798", "from":currency, "to":this_wallet_user_currency, "amount":amount})
        
        if res.status_code == 200:
            data = res.json()
        
            amount_out = data['result']
            rounded_amount = round(amount_out, 2)
        if wallet.balance >= rounded_amount:
            if curr_user.id != this_wallet_user.id:
                if curr_user.role_id == 1:
                    wallet.balance -= rounded_amount
                    db.session.merge(wallet)
                    db.session.commit()
                    return wallet_schema.jsonify(wallet)
                return {"error" : "you do not have the facilities to perfrom this action"}

            if curr_user.id == this_wallet_user.id:
                if curr_user.role_id == 3:
                    wallet.balance -= rounded_amount
                    db.session.merge(wallet)
                    db.session.commit()

                    return wallet_schema.jsonify(wallet)
        else:
            return {"error": "your balance is too low for this transaction"}
        return {"error": "this wallet is not available to you"}
    except:
        return {"error": "kindly cross-check your inputs"}


@app.route("/approve/<id>", methods=['POST'])
@jwt_required
def approve(id):
    username = request.json['username']
    approved = request.json['approved']

    logged_in_id = get_jwt_identity()
    curr_user = User.query.get(logged_in_id)

    user = User.query.filter_by(username=username).first()
    wallet = Wallets.query.filter_by(user_id=user.id).first()
    approve = PendingApproval.query.get(id)

    print(approve)
    if curr_user.role_id == 1:
        approve.approved = approved
        if approve.approved is True:
            wallet.balance+=approve.pending_balance
            approve.pending_balance = 0.00
            db.session.merge(approve)
            db.session.merge(wallet)
            db.session.commit()

            return {"status": "approved"}
        return {"status" : "not approved"}
    return {"error": "you do not have the authority to make approval"}


    

if __name__ == '__main__':
    import os
    HOST = os.environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(os.environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555
    app.run(HOST, PORT)
