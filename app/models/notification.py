from app.extensions import db
from . import BaseModel

class Notification(BaseModel):
    __tablename__ = 'notifications'

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    message = db.Column(db.String(255), nullable=False)
    read = db.Column(db.Boolean, default=False, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now(), index=True)
    
    user = db.relationship('User', backref=db.backref('notifications', lazy='subquery'), lazy='joined')
