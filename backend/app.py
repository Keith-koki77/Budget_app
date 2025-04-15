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