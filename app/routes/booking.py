from flask import Blueprint, request, current_app # Import current_app
from app.services.booking_service import BookingService
from app.utils.response import success, error_response
from app.utils.decorators import jwt_required
from app.utils.validators import validate_request
from app.extensions import db # Import db for transaction management

booking_bp = Blueprint('booking', __name__, url_prefix='/bookings')

@booking_bp.route('', methods=['POST'])
@jwt_required
@validate_request('pickup_address', 'dropoff_address', 'booking_time')
def create_booking(current_user):
    data = request.get_json()
    try:
        booking = BookingService.create_booking(current_user, data)
        db.session.commit() # Commit the transaction after successful service operation
        return success(booking.to_dict(), 201)
    except ValueError as e: # Catch specific validation errors from service
        db.session.rollback()
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback() # Rollback in case of any other unexpected error
        current_app.logger.error(f"An unexpected error occurred while creating the booking: {e}", exc_info=True) # Log the full error
        return error_response("An unexpected error occurred while creating the booking.", 500)

@booking_bp.route('/<int:booking_id>', methods=['GET'])
@jwt_required
def get_booking(current_user, booking_id):
    try:
        booking = BookingService.get_booking_by_id(booking_id, current_user)
        return success(booking.to_dict())
    except ValueError as e: # Catch specific errors from service (e.g., "Booking not found", "Unauthorized")
        return error_response(str(e), 404) # Or 403 for unauthorized specific cases
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred while getting booking {booking_id}: {e}", exc_info=True)
        return error_response("An unexpected error occurred while retrieving the booking.", 500)
