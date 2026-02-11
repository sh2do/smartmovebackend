from app.extensions import db, bcrypt
from . import BaseModel
import enum

class UserRole(enum.Enum):
    CUSTOMER = 'customer'
    MOVER = 'mover'
    ADMIN = 'admin'

class User(BaseModel):
    __tablename__ = 'users'

    first_name = db.Column(db.String(100), nullable=True) # Making nullable=True for existing users
    last_name = db.Column(db.String(100), nullable=True)  # Making nullable=True for existing users
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    role = db.Column(db.Enum(UserRole), default=UserRole.CUSTOMER, nullable=False, index=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), server_onupdate=db.func.now())

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def to_dict(self):
        data = super().to_dict()
        data.pop('password_hash', None)
        return data
