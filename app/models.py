from . import db
from datetime import datetime

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    batch_no = db.Column(db.String(15), nullable=False)
    name = db.Column(db.String(25), nullable=False)
    description = db.Column(db.String(20), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    mrp = db.Column(db.Float, nullable=False)
    expiry_date = db.Column(db.Date, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    hsn = db.Column(db.String(20), default="30049069")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Invoice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_no = db.Column(db.String(10), unique=True, nullable=False)
    customer_name = db.Column(db.String(50))
    customer_phone = db.Column(db.String(10))
    total_amount = db.Column(db.Float)
    discount = db.Column(db.Float)
    final_amount = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    items = db.relationship('InvoiceItem', backref='invoice', lazy=True)

class InvoiceItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    invoice_id = db.Column(db.Integer, db.ForeignKey('invoice.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('product.id'))
    product_name = db.Column(db.String(50))
    batch_no = db.Column(db.String(15))
    price = db.Column(db.Float)
    quantity = db.Column(db.Integer)
    total = db.Column(db.Float)
