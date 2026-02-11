import datetime
from app.extensions import db
from app.models.booking import Booking, BookingStatus, PaymentStatus
from app.models.address import Address
from app.models.user import User # To get user info if needed, or current_user is already User object

class BookingService:
    @staticmethod
    def create_booking(current_user: User, data):
        pickup_address_str = data.get('pickup_address')
        dropoff_address_str = data.get('dropoff_address')
        booking_time_str = data.get('booking_time')
        mover_id = data.get('mover_id') # Optional, mover can be assigned later

        if not all([pickup_address_str, dropoff_address_str, booking_time_str]):
            raise ValueError("Pickup address, dropoff address, and booking time are required.")

        # Assume addresses are simple strings for now, convert to Address objects
        # In a real app, you might have an AddressService to handle creation/lookup
        pickup_address = Address(street=pickup_address_str, city='Unknown', state='Unknown', zip_code='Unknown', user_id=current_user.id)
        dropoff_address = Address(street=dropoff_address_str, city='Unknown', state='Unknown', zip_code='Unknown', user_id=current_user.id)
        
        # Convert booking_time string to datetime object
        try:
            # Assuming ISO format like "YYYY-MM-DDTHH:MM:SS" or similar
            booking_time = datetime.datetime.fromisoformat(booking_time_str)
        except ValueError:
            raise ValueError("Invalid booking time format. Expected ISO format.")

        new_booking = Booking(
            user_id=current_user.id,
            mover_id=mover_id, # Can be None if mover assigned later
            pickup_address=pickup_address,
            dropoff_address=dropoff_address,
            booking_time=booking_time,
            status=BookingStatus.PENDING,
            payment_status=PaymentStatus.PENDING,
            amount=0.00 # Placeholder amount, would be calculated by pricing service
        )

        db.session.add(new_booking)
        db.session.add(pickup_address)
        db.session.add(dropoff_address)
        # db.session.commit() is now handled by the route or transaction manager

        return new_booking

    @staticmethod
    def get_booking_by_id(booking_id: int, current_user: User):
        booking = Booking.query.get(booking_id)
        if not booking:
            raise ValueError("Booking not found.")
        
        # Authorization: Ensure user can view this booking
        if booking.user_id != current_user.id and \
           (current_user.role != User.UserRole.ADMIN and \
            (current_user.role != User.UserRole.MOVER or (current_user.mover and booking.mover_id != current_user.mover.id))):
            raise ValueError("Unauthorized to view this booking.") # Or a more specific exception like ForbiddenError

        return booking