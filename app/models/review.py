from app.extensions import db
from . import BaseModel

class Review(BaseModel):
    __tablename__ = 'reviews'

    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mover_id = db.Column(db.Integer, db.ForeignKey('movers.id'), nullable=False)
    
    rating = db.Column(db.Integer, nullable=False, index=True)
    comment = db.Column(db.Text)
    
    booking = db.relationship('Booking', backref='review')
    user = db.relationship('User', backref='reviews')
    mover = db.relationship('Mover', backref='reviews')
