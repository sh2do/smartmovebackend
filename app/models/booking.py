from app.extensions import db
from . import BaseModel
import enum

class PaymentStatus(enum.Enum):
    PENDING = 'pending'
    COMPLETED = 'completed'
    FAILED = 'failed'

class BookingStatus(enum.Enum):
    PENDING = 'pending'
    CONFIRMED = 'confirmed'
    IN_PROGRESS = 'in_PROGRESS'
    COMPLETED = 'completed'
    CANCELLED = 'cancelled'

class Booking(BaseModel):
    __tablename__ = 'bookings'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    mover_id = db.Column(db.Integer, db.ForeignKey('movers.id'), nullable=False, index=True)
    
    pickup_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False, index=True)
    dropoff_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False, index=True)
    
    booking_time = db.Column(db.DateTime(timezone=True), nullable=False, index=True)
    status = db.Column(db.Enum(BookingStatus), default=BookingStatus.PENDING, nullable=False, index=True)
    
    amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.00)
    mpesa_receipt_number = db.Column(db.String(20), nullable=True)
    payment_status = db.Column(db.Enum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    checkout_request_id = db.Column(db.String(50), nullable=True, index=True)
    
    user = db.relationship('User', backref=db.backref('bookings', lazy='subquery'), lazy='joined')
    mover = db.relationship('Mover', backref=db.backref('bookings', lazy='subquery'), lazy='joined')
    
    pickup_address = db.relationship('Address', foreign_keys=[pickup_address_id], lazy='joined')
    dropoff_address = db.relationship('Address', foreign_keys=[dropoff_address_id], lazy='joined')
