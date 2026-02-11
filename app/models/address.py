from app.extensions import db
from . import BaseModel

class Address(BaseModel):
    __tablename__ = 'addresses'

    street = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(20), nullable=False, index=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
