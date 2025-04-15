"""
Budgeting App Backend
______________________

This backend implements:
  - User registration (with a default daily expenditure cap)
  - A digital wallet to keep track of balance and expenditures
  - Simulated deposit endpoint to accept funds from "paypal" or "bank" sources
  - Expense recording ensuring the daily cap is not exceeded
  - Transaction history tied to dates (calendar)

Requred librarie: Flask, Flask-SQLAlchemy
Install via: pip install Flask Flask-SQLAlchemy
"""

import os
from decimal import Decimal
from datetime import datetime, date

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

# Initialize Flask app and configure the SQLite database
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://budgeting_app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

#-----------------------------
# DATABASE MODELS
#------------------------------

class User(db.Model):
    """
    User Model Reperesenting an app user.
    """
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcown)
    # One-to-one relationship with Wallet
    wallet = db.relationship('Wallet', backref='user', uselist=False, cascade="all, delete-orphan")

class Wallet(db.Model):
    """
    Wallet Model Containing balance and Daily Expenditure cap.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    balance = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    daily_cap = db.Column(db.Number(10, 2), nullable=False, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    transactions = db.relationship('Transaction', backref='wallet', cascade="all, delete-orphan", lazy=True)

class Transaction(db.Model):
    """
    Transaction Model for Deposits and expenses.
    """
    id = db.Column(db.Integer, primary_key=True)
    wallet_id = db.Column(db.Integer, db.Foreign('wallet.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    transaction_type = db.Column(db.String(20), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(255))
    provider = db.Column(db.String(50))


# --------------------------------
# HELPER FUNCTIONS
# --------------------------------

def get_daily_expense(wallet_id, for_date):
    """
    Return the Total Expense for a given wallet on the specified date.
    """
    daily_total = db.session.query(
        db.func.coalesce(db.func.sum(Transaction.amount), 0)
    ).filter(
        Transaction.wallet_id == wallet_id,
        Transaction.transaction_type == 'expense',
        db.func.date(Transaction.timestamp) == for_date        
    ).scalar()
    return Decimal(daily_total)


# -------------------------------------
# API ENDPOINTS
# -------------------------------------

@app.route('/register', methods=['POST'])
def register():
    """
    Register a new user.
    Expected JSON payload:
        { "username": "user1", "daily_cap": "150.00"} # Daily cap is optional (default=100)
    """
    data = request.get_json() or {}
    username = data.get("username")
    daily_cap = data.get("daily_cap", "100.00")

    if not username:
        return jsonify({"error": "username is required"}), 400
    
    # Create and save the new user
    user = User(username=username)
    db.session.add(user)
    db.session.commit()

    # Create an associated wallet with a starting balance of 0 abd the provided daily cap.
    try:
        daily_cap_decimal = Decimal(daily_cap)
    except Exception:
        return jsonify({"error": "Invalid daily_cap format"}), 400
    
    wallet = Wallet(user_id=user.id, balance=Decimal('0.00'), daily_cap=daily_cap_decimal)
    db.session.add(wallet)
    db.session.commit()

    return jsonify({
        "message": "User registered successfully",
        "user_id": user.id,
        "wallet_id": wallet.id,
        "daily_cap": str(wallet.daily_cap)
    }), 201

@app.route('/deposit', methods=['POST'])
def deposit():
    """
    Endpoint to deposit funds into the wallet.
    Expected JSON payload:
        { "wallet_id": 1, "provider": "paypal", "amount": "50.00" }
    """
    data = request.get_json() or {}
    wallet_id = data.get("wallet_id")
    provider = data.get("provider")
    amount = data.get("amount")

    if not wallet_id or not provider or not amount:
        return jsonify({"error": "wallet_id, provider, and amount are required"}), 400
    
    wallet = Wallet.query.get(wallet_id)
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404
    
    try:
        amount_dec = Decimal(amount)
    except Exception:
        return jsonify({"error": "Invalid amount format"}), 400
    
    # Update the wallet balance and record the deposit transaction
    wallet.balance += amount_dec
    transaction = Transaction(
        wallet_id=wallet.id,
        amount=amount_dec,
        transaction_type='deposit',
        provider=provider,
        description=f"Deposit via {provider}",
        timestamp=datetime.utcnow()
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "message": "Deposit successful",
        "new_balance": str(wallet.balance)
    }), 200

@app.route('/spend', methods=['POST'])
def spend():
    """
    Endpoint to record an expense.
    Expected JSON payload:
        { "wallet_id": 1, "amount": "20.00", "description": "Lunch" }
    
    Enforces the daily spending cap.
    """
    data = request.get_json() or {}
    wallet_id = data.get("wallet_id")
    amount = data.get("amount")
    description = data.get("description", "Expense")

    if not wallet_id or not amount:
        return jsonify({"error": "wallet_id and amount are required"}), 400
    
    wallet = Wallet.query.get(wallet_id)
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404
    
    try:
        amount_dec = Decimal(amount)
    except Exception:
        return jsonify({"error": "Invalid amount format"}), 400
    
    # Check if sufficient balance exixtx
    if wallet.balance < amount_dec:
        return jsonify({"error": "Insufficient funds"}), 400
    
    # Calculate today's total expense and enforce daily cap limit
    today = date.today()
    current_daily_spent = get_daily_expense(wallet.id, today)
    if current_daily_spent + amount_dec > wallet.daily_cap:
        return jsonify({
            "error": "Daily cap exceeded",
            "daily_cap": str(wallet.daily_cap),
            "already_spent": str(current_daily_spent)
        }), 400
    
    # Deduct the expense from the wallet and record the transaction
    wallet.balance -= amount_dec
    transaction = Transaction(
        wallet_id=wallet.id,
        amount=amount_dec,
        transaction_type='expense',
        description=description,\
        timestamp=datetime.utcnow()
    )
    db.session.add(transaction)
    db.session.commit()

    return jsonify({
        "message": "Expense recorded successfully",
        "new_balance": str(wallet.balance)
    }), 200

@app.route('/transactions/<int:wallet_id>', methods=['GET'])
def transactions(wallet_id):
    """
    Get transcation history for a wallet.
    Optional query paramater: date (YYYY-MM-DD)
    Example: /transactions/?date=2025-04-15
    """
    wallet = Wallet.query.get(wallet_id)
    if not wallet:
        return jsonify({"error": "Wallet not found"}), 404
    
    query = Transaction.query.filter_by(wallet_id=wallet_id)
    filter_date = request.args.get("date")

    if filter_date:
        try:
            filter_date_obj = datetime.strptime(filter_date, "%Y-%m-%d").date()
        except ValueError:
            return jsonify({"error": "Invalid date format. Use YYYY-MM-DD"}), 400
        query = query.filter(db.func.date(Transaction.timestamp) == filter_date_obj)

    transactions_list = query.order_by(Transaction.timestamp.desc()).all()

    # Format transcation records for response
    result = [{
        "id": t.id,
        "amount": str(t.amount),
        "type": t.transaction_type,
        "timestamp": t.timestamp.isoformat(),
        "description": t.description,
        "provider": t.provider
    } for t in transactions_list]

    return jsonify(result), 200