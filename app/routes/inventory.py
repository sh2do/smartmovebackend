from flask import Blueprint, request, current_app, g # Import g
from app.utils.response import success, error_response
from app.utils.decorators import jwt_required
from app.utils.validators import validate_request
from app.services.inventory_service import InventoryService # Import InventoryService
from app.extensions import db # Import db for transaction management

inventory_bp = Blueprint('inventory', __name__, url_prefix='/inventory')

@inventory_bp.route('', methods=['GET'])
@jwt_required
def get_user_inventory():
    """
    Retrieves the inventory for the current user.
    """
    current_user = g.current_user
    try:
        user_inventory = InventoryService.get_user_inventory(current_user)
        return success([item.to_dict() for item in user_inventory])
    except Exception as e:
        current_app.logger.error(f"Error retrieving user inventory for user {current_user.id}: {e}", exc_info=True)
        return error_response("An unexpected error occurred while retrieving inventory.", 500)
    

@inventory_bp.route('', methods=['POST'])
@jwt_required
@validate_request('name', 'quantity', 'booking_id') # Added booking_id to validate_request
def add_inventory_item():
    """
    Adds an item to the user's inventory.
    """
    current_user = g.current_user
    data = request.get_json()
    
    try:
        new_item = InventoryService.add_inventory_item(current_user, data)
        db.session.commit()
        return success(new_item.to_dict(), 201)
    except ValueError as e:
        db.session.rollback()
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error adding inventory item for user {current_user.id}: {e}", exc_info=True)
        return error_response("An unexpected error occurred while adding inventory item.", 500)
    
