from app.extensions import db
from . import BaseModel

class Mover(BaseModel):
    __tablename__ = 'movers'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    company_name = db.Column(db.String(120), index=True)
    bio = db.Column(db.Text)
    service_area = db.Column(db.String(255))
    approved = db.Column(db.Boolean, default=False, index=True)
    
    user = db.relationship('User', backref=db.backref('mover', uselist=False, lazy='joined'), lazy='joined')
