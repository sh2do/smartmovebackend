import enum
from app.extensions import db

class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)

    def save(self):
        db.session.add(self)

    def delete(self):
        db.session.delete(self)

    def to_dict(self):
        d = {}
        for c in self.__table__.columns:
            val = getattr(self, c.name)
            if isinstance(val, enum.Enum):
                d[c.name] = val.value
            else:
                d[c.name] = val
        return d

# Import all models here
from .user import User
from .mover import Mover
from .address import Address
from .booking import Booking
from .review import Review
from .inventory import Inventory
from .chat import Message
from .notification import Notification
from .quote import Quote
