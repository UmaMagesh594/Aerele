from app import db
from sqlalchemy.sql import func

class Product(db.Model):
    __tablename__ = 'product'
    product_id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Product {self.product_id} - {self.name}>'

class Location(db.Model):
    __tablename__ = 'location'
    location_id = db.Column(db.String(64), primary_key=True)
    name = db.Column(db.String(255), nullable=False)

    def __repr__(self):
        return f'<Location {self.location_id} - {self.name}>'

class ProductMovement(db.Model):
    __tablename__ = 'product_movement'
    movement_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    timestamp = db.Column(db.DateTime, default=func.now())
    from_location = db.Column(db.String(64), db.ForeignKey('location.location_id'), nullable=True)
    to_location = db.Column(db.String(64), db.ForeignKey('location.location_id'), nullable=True)
    product_id = db.Column(db.String(64), db.ForeignKey('product.product_id'), nullable=False)
    qty = db.Column(db.Integer, nullable=False)

    # optional relationships for convenience
    product = db.relationship('Product', backref='movements')
    from_loc = db.relationship('Location', foreign_keys=[from_location])
    to_loc = db.relationship('Location', foreign_keys=[to_location])

    def __repr__(self):
        return f'<Movement {self.movement_id} {self.product_id} {self.qty}>'
