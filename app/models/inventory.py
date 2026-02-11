from app.extensions import db
from . import BaseModel

class Inventory(BaseModel):
    __tablename__ = 'inventories'

    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, index=True)
    name = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    
    booking = db.relationship('Booking', backref=db.backref('inventory_items', lazy='subquery'), lazy='joined')
