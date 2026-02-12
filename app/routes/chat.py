from flask import Blueprint, request, current_app, g # Import g
from app.utils.response import success, error_response
from app.utils.decorators import jwt_required
from app.services.chat_service import ChatService # Import ChatService
from app.extensions import db # Import db for transaction management

chat_bp = Blueprint('chat', __name__, url_prefix='/chats')

@chat_bp.route('', methods=['POST'])
@jwt_required
def create_chat_session():
    """
    Starts a new chat session.
    """
    current_user = g.current_user
    data = request.get_json()
    if not data or 'recipient_id' not in data:
        return error_response("Recipient ID is required.", 400)
        
    recipient_id = data['recipient_id']
    
    try:
        # ChatService will validate recipient and return a success message for now
        # In a real app, this would create a ChatSession object
        chat_session_info = ChatService.create_chat_session(current_user, recipient_id)
        # No db.session.commit() here, as ChatService.create_chat_session doesn't add to DB yet
        return success(chat_session_info, 201)
    except ValueError as e:
        return error_response(str(e), 400)
    except Exception as e:
        current_app.logger.error(f"Error creating chat session: {e}", exc_info=True)
        return error_response("An unexpected error occurred while starting chat session.", 500)


@chat_bp.route('/<string:chat_session_id>/messages', methods=['POST'])
@jwt_required
def send_message(chat_session_id):
    """
    Sends a message within a chat session.
    """
    current_user = g.current_user
    data = request.get_json()
    
    if not data or 'message_body' not in data:
        return error_response("Message body is required.", 400)
    
    message_body = data['message_body']
    
    try:
        new_message = ChatService.send_message(current_user, chat_session_id, message_body)
        db.session.commit() # Commit the transaction after successful service operation
        return success(new_message.to_dict(), 201)
    except ValueError as e:
        db.session.rollback()
        return error_response(str(e), 400)
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Error sending message in chat session {chat_session_id}: {e}", exc_info=True)
        return error_response("An unexpected error occurred while sending the message.", 500)
