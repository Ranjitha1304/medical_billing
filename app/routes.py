from flask import Blueprint, render_template, request, redirect, url_for
from .models import Product
from . import db
from datetime import datetime, date
import json
from .models import Invoice, InvoiceItem
from sqlalchemy import extract
from collections import defaultdict
import calendar

main = Blueprint('main', __name__)

@main.route("/")
def overview():
    products = Product.query.all()
    
    # Revenue (monthly)
    this_month = datetime.today().month
    this_year = datetime.today().year

    monthly_invoices = Invoice.query.filter(
        extract('month', Invoice.created_at) == this_month,
        extract('year', Invoice.created_at) == this_year).all()

    total_revenue = sum(inv.final_amount for inv in monthly_invoices)

    # Stock summaries
    total_stock = sum(p.stock for p in products)
    out_of_stock = sum(1 for p in products if p.stock == 0)
    expired = sum(1 for p in products if p.expiry_date < date.today())

    # Purchase report (daily)
    today = date.today()
    today_invoices = Invoice.query.filter(db.func.date(Invoice.created_at) == today).all()
    today_invoice_ids = [inv.id for inv in today_invoices]

    today_items = db.session.query(db.func.sum(InvoiceItem.quantity)).filter(
        InvoiceItem.invoice_id.in_(today_invoice_ids)
    ).scalar() or 0

    today_amount = sum(inv.final_amount for inv in today_invoices)


    # Prepare monthly sales data (12 months)
    monthly_totals = defaultdict(float)
    invoices = Invoice.query.all()

    for invoice in invoices:
        key = invoice.created_at.strftime('%b')  # e.g., 'Jan', 'Feb'
        monthly_totals[key] += invoice.final_amount

    # Ensure all 12 months are present (in order)
    
    months = list(calendar.month_abbr)[1:]  # ['Jan', ..., 'Dec']
    monthly_sales = [round(monthly_totals.get(month, 0)) for month in months]    

    return render_template("overview.html", title="Dashboard | Kani Medicals",
                           total_revenue=total_revenue,
                           total_stock=total_stock,
                           out_of_stock=out_of_stock,
                           expired=expired,
                           today_items=today_items,
                           today_amount=round(today_amount),
                           months=months,
                           monthly_sales=monthly_sales)


@main.route("/add-product", methods=["GET", "POST"])
def add_product():
    if request.method == "POST":
        batch_no = request.form['batch_no']
        name = request.form['name']
        description = request.form['description']
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])

        # Extract only month and year from expiry input (e.g. "2025-11")
        expiry_input = request.form['expiry_date'] + "-01"  # make it a full date
        expiry_date = datetime.strptime(expiry_input, "%Y-%m-%d").date()

        stock = int(request.form['stock'])
        mrp = float(request.form['mrp'])
        hsn = request.form.get('hsn', "30049069")

        # Check for existing product with same name, batch_no and same expiry (month & year)
        existing_product = Product.query.filter(
            Product.name == name,
            Product.batch_no == batch_no,
            extract('month', Product.expiry_date) == expiry_date.month,
            extract('year', Product.expiry_date) == expiry_date.year
        ).first()

        if existing_product:
            existing_product.stock += stock
            existing_product.quantity += quantity
            db.session.commit()
        else:
            product = Product(
                batch_no=batch_no, name=name, description=description,
                quantity=quantity, price=price, expiry_date=expiry_date,
                stock=stock, mrp=mrp, hsn=hsn
            )
            db.session.add(product)
            db.session.commit()

        return redirect(url_for('main.products'))

    return render_template("add_product.html", title="Add Product | Kani Medicals", current_date=date.today())

@main.route("/products")
def products():
    all_products = Product.query.order_by(Product.id.desc()).all()
    return render_template("products.html", title="Products | Kani Medicals", products=all_products)



@main.route('/billing', methods=["GET"])
def billing():
    today = date.today()
    invoice_count = Invoice.query.count() + 1
    invoice_no = f"INV{invoice_count:02d}"
    return render_template("billing.html",
                           title="Billing | Kani Medicals",
                           current_date=today.strftime("%Y-%m-%d"),
                           invoice_no=invoice_no)

@main.route("/generate-bill", methods=["POST"])
def generate_bill():
    data = request.form
    cart_data = json.loads(data['cart_data'])
    if not cart_data:
        return redirect(url_for('main.billing'))  # prevent going to invoice if cart is empty


    invoice = Invoice(
        invoice_no=data['invoice_no'],
        customer_name=data['customer_name'],
        customer_phone=data['customer_phone'],
        discount = float(data.get('discount') or 0),
        total_amount=0,
        final_amount=0
    )
    total = 0
    db.session.add(invoice)
    db.session.commit()

    for i, item in enumerate(cart_data):
        subtotal = float(item['price']) * int(item['quantity'])
        invoice_item = InvoiceItem(
            invoice_id=invoice.id,
            product_id=item['id'],
            product_name=item['name'],
            batch_no=item['batch_no'],
            price=float(item['price']),
            quantity=int(item['quantity']),
            total=subtotal
        )
        total += subtotal
        db.session.add(invoice_item)

        # Reduce product stock
        product = Product.query.get(item['id'])
        product.stock -= int(item['quantity'])

    invoice.total_amount = total
    invoice.final_amount = round(total - (total * invoice.discount / 100))
    db.session.commit()

    return redirect(url_for('main.invoice', id=invoice.id))


@main.route('/invoice/<int:id>')
def invoice(id):
    invoice = Invoice.query.get_or_404(id)
    return render_template('invoice.html', invoice=invoice)

