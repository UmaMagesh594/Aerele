from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET', 'dev-secret')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///inventory.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

from models import Product, Location, ProductMovement

with app.app_context():
    db.create_all()

@app.route('/products')
def list_products():
    products = Product.query.order_by(Product.product_id).all()
    return render_template('products.html', products=products)

@app.route('/products/add', methods=['GET','POST'])
def add_product():
    if request.method == 'POST':
        pid = request.form['product_id'].strip()
        name = request.form['name'].strip()
        if not pid or not name:
            flash('Product ID and name required', 'danger')
            return redirect(url_for('add_product'))
        if Product.query.get(pid):
            flash('Product ID already exists', 'danger')
            return redirect(url_for('add_product'))
        p = Product(product_id=pid, name=name)
        db.session.add(p)
        db.session.commit()
        flash('Product added', 'success')
        return redirect(url_for('list_products'))
    return render_template('product_form.html', product=None)

@app.route('/products/edit/<product_id>', methods=['GET','POST'])
def edit_product(product_id):
    p = Product.query.get_or_404(product_id)
    if request.method == 'POST':
        p.name = request.form['name'].strip()
        db.session.commit()
        flash('Product updated', 'success')
        return redirect(url_for('list_products'))
    return render_template('product_form.html', product=p)

@app.route('/products/delete/<product_id>', methods=['POST'])
def delete_product(product_id):
    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash(f'Product {product_id} deleted successfully', 'success')
    return redirect(url_for('list_products'))

@app.route('/locations')
def list_locations():
    locations = Location.query.order_by(Location.location_id).all()
    return render_template('locations.html', locations=locations)

@app.route('/locations/add', methods=['GET','POST'])
def add_location():
    if request.method == 'POST':
        lid = request.form['location_id'].strip()
        name = request.form['name'].strip()
        if not lid or not name:
            flash('Location ID and name required', 'danger')
            return redirect(url_for('add_location'))
        if Location.query.get(lid):
            flash('Location ID already exists', 'danger')
            return redirect(url_for('add_location'))
        loc = Location(location_id=lid, name=name)
        db.session.add(loc)
        db.session.commit()
        flash('Location added', 'success')
        return redirect(url_for('list_locations'))
    return render_template('location_form.html', location=None)

@app.route('/locations/edit/<location_id>', methods=['GET','POST'])
def edit_location(location_id):
    loc = Location.query.get_or_404(location_id)
    if request.method == 'POST':
        loc.name = request.form['name'].strip()
        db.session.commit()
        flash('Location updated', 'success')
        return redirect(url_for('list_locations'))
    return render_template('location_form.html', location=loc)

@app.route('/locations/delete/<location_id>', methods=['POST'])
def delete_location(location_id):
    location = Location.query.get_or_404(location_id)

    used_in_movement = (
        db.session.query(ProductMovement)
        .filter(
            (ProductMovement.from_location == location_id)
            | (ProductMovement.to_location == location_id)
        )
        .first()
    )
    if used_in_movement:
        flash('Cannot delete location: it is referenced in a product movement.', 'danger')
        return redirect(url_for('list_locations'))

    db.session.delete(location)
    db.session.commit()
    flash(f'Location {location_id} deleted successfully', 'success')
    return redirect(url_for('list_locations'))

@app.route('/movements')
def list_movements():
    movements = ProductMovement.query.order_by(ProductMovement.timestamp.desc()).limit(200).all()
    return render_template('movements.html', movements=movements)

@app.route('/movements/add', methods=['GET','POST'])
def add_movement():
    products = Product.query.order_by(Product.name).all()
    locations = Location.query.order_by(Location.name).all()
    if request.method == 'POST':
        product_id = request.form.get('product_id')
        qty = int(request.form.get('qty', '0') or 0)
        from_loc = request.form.get('from_location') or None
        to_loc = request.form.get('to_location') or None
        if not product_id or qty <= 0:
            flash('Product and positive qty required', 'danger')
            return redirect(url_for('add_movement'))
        mv = ProductMovement(
            timestamp=datetime.utcnow(),
            from_location=from_loc,
            to_location=to_loc,
            product_id=product_id,
            qty=qty
        )
        db.session.add(mv)
        db.session.commit()
        flash('Movement recorded', 'success')
        return redirect(url_for('list_movements'))
    return render_template('movement_form.html', products=products, locations=locations)

@app.route('/report')
def report():
    products = Product.query.order_by(Product.name).all()
    locations = Location.query.order_by(Location.name).all()

    balances = {}
    for p in products:
        for l in locations:
            balances[(p.product_id, l.location_id)] = 0

    movements = ProductMovement.query.order_by(ProductMovement.timestamp).all()
    for m in movements:
        pid = m.product_id
        q = m.qty or 0
        if m.to_location:
            balances[(pid, m.to_location)] = balances.get((pid, m.to_location), 0) + q
        if m.from_location:
            balances[(pid, m.from_location)] = balances.get((pid, m.from_location), 0) - q

    grid = []
    for p in products:
        for l in locations:
            qty = balances.get((p.product_id, l.location_id), 0)
            grid.append({'product': p, 'location': l, 'qty': qty})

    return render_template('report.html', grid=grid, products=products, locations=locations)

@app.route('/')
def home():
    return redirect(url_for('report'))

if __name__ == '__main__':
    app.run(debug=True)
