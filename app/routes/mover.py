from flask import Blueprint, request, current_app, g # Import g
from app.services.mover_service import MoverService
from app.utils.response import success, error_response
from app.utils.decorators import jwt_required, roles_required
from app.extensions import db # Import db for transaction management

mover_bp = Blueprint('mover', __name__, url_prefix='/movers')

@mover_bp.route('/profile', methods=['PUT'])
@jwt_required
@roles_required('mover')
def update_mover_profile():
    current_user = g.current_user
    data = request.get_json()
    try:
        mover = MoverService.update_mover_profile(current_user.mover.id, data)
        db.session.commit() # Commit the transaction after successful service operation
        return success(mover.to_dict())
    except ValueError as e: # Catch specific errors from service (e.g., Mover not found)
        db.session.rollback()
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback() # Rollback in case of any other unexpected error
        current_app.logger.error(f"An unexpected error occurred while updating mover profile {current_user.mover.id}: {e}", exc_info=True)
        return error_response("An unexpected error occurred while updating the mover profile.", 500)
@mover_bp.route('/availability', methods=['GET'])
@jwt_required
@roles_required('mover')
def get_availability():
    current_user = g.current_user
    try:
        availability = MoverService.get_availability(current_user.mover.id)
        return success(availability)
    except ValueError as e: # Catch specific errors from service (e.g., Mover not found)
        return error_response(str(e), 404)
    except Exception as e:
        current_app.logger.error(f"An unexpected error occurred while getting availability for mover {current_user.mover.id}: {e}", exc_info=True)
        return error_response("An unexpected error occurred while retrieving mover availability.", 500)
