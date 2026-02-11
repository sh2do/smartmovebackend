from app.extensions import db
from . import BaseModel

class Review(BaseModel):
    __tablename__ = 'reviews'

    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    mover_id = db.Column(db.Integer, db.ForeignKey('movers.id'), nullable=False, index=True)
    
    rating = db.Column(db.Integer, nullable=False, index=True)
    comment = db.Column(db.Text)
    
    booking = db.relationship('Booking', backref=db.backref('review', lazy='joined'), lazy='joined')
    user = db.relationship('User', backref=db.backref('reviews', lazy='subquery'), lazy='joined')
    mover = db.relationship('Mover', backref=db.backref('reviews', lazy='subquery'), lazy='joined')
