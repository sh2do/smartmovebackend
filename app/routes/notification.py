from flask import Blueprint, g # Import g
from app.utils.response import success, error_response
from app.utils.decorators import jwt_required
from app.models.notification import Notification

notification_bp = Blueprint('notification', __name__, url_prefix='/notifications')

@notification_bp.route('', methods=['GET'])
@jwt_required
def get_notifications():
    """
    Retrieves all notifications for the current user.
    """
    current_user = g.current_user
    try:
        notifications = Notification.query.filter_by(user_id=current_user.id).all()
        return success([notification.to_dict() for notification in notifications])
    except Exception as e:
        return error_response(str(e), 500)

@notification_bp.route('/<int:notification_id>/read', methods=['PUT'])
@jwt_required
def mark_as_read(notification_id):
    """
    Marks a specific notification as read.
    """
    current_user = g.current_user
    try:
        notification = Notification.query.filter_by(id=notification_id, user_id=current_user.id).first_or_404()
        notification.is_read = True
        notification.save()
        return success({"message": "Notification marked as read."})
    except Exception as e:
        return error_response(str(e), 500)
