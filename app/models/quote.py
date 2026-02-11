from app.extensions import db
from . import BaseModel
import enum

class QuoteStatus(enum.Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    REJECTED = 'rejected'

class Quote(BaseModel):
    __tablename__ = 'quotes'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    mover_id = db.Column(db.Integer, db.ForeignKey('movers.id'), nullable=True)

    pickup_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False)
    dropoff_address_id = db.Column(db.Integer, db.ForeignKey('addresses.id'), nullable=False)

    distance_meters = db.Column(db.Integer, nullable=False)
    volume_cubic_meters = db.Column(db.Float, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.Enum(QuoteStatus), default=QuoteStatus.PENDING, nullable=False, index=True)

    user = db.relationship('User', backref='quotes')
    mover = db.relationship('Mover', backref='quotes')

    pickup_address = db.relationship('Address', foreign_keys=[pickup_address_id])
    dropoff_address = db.relationship('Address', foreign_keys=[dropoff_address_id])
