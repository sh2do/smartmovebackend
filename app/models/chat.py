from app.extensions import db
from . import BaseModel

class Message(BaseModel):
    __tablename__ = 'messages'

    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, server_default=db.func.now(), index=True)
    
    booking = db.relationship('Booking', backref='messages')
    user = db.relationship('User', backref='messages')
