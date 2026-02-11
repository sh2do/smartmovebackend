import datetime
from app.extensions import db
from app.models.chat import Message
from app.models.user import User # Assuming sender/recipient are users

class ChatService:
    @staticmethod
    def create_chat_session(current_user: User, recipient_id: int):
        # For simplicity, a chat session is implicitly created by the first message
        # or can be a separate model. Here, we'll just validate recipient exists.
        recipient = User.query.get(recipient_id)
        if not recipient:
            raise ValueError("Recipient not found.")
        
        if current_user.id == recipient_id:
            raise ValueError("Cannot start a chat session with yourself.")
        
        # In a real app, you'd check for existing session or create a new ChatSession model.
        # For now, we'll return a simple indication of success.
        return {"status": "success", "message": "Chat session can proceed."}

    @staticmethod
    def send_message(current_user: User, chat_session_id: str, message_body: str):
        # Assuming chat_session_id is a unique identifier, potentially for a Booking.
        # For now, we'll link messages directly to a booking_id as a simple session.
        # In a real app, you'd look up a ChatSession model using chat_session_id.
        try:
            booking_id = int(chat_session_id) # Attempt to interpret as booking_id
        except ValueError:
            raise ValueError("Invalid chat_session_id format. Expected an integer booking ID for now.")

        # Validate that the current user is part of this booking (as user or mover)
        # This is a simplification; a dedicated ChatSession model would link users
        from app.models.booking import Booking # Import here to avoid circular import

        booking = Booking.query.get(booking_id)
        if not booking:
            raise ValueError("Chat session (booking) not found.")

        # Ensure current_user is involved in this booking
        if booking.user_id != current_user.id and \
           (current_user.role != User.UserRole.ADMIN and \
            (current_user.role != User.UserRole.MOVER or (current_user.mover and booking.mover_id != current_user.mover.id))):
            raise ValueError("Unauthorized to send message in this chat session.")

        new_message = Message(
            booking_id=booking_id,
            user_id=current_user.id,
            content=message_body,
            timestamp=datetime.datetime.now()
        )
        db.session.add(new_message)
        # db.session.commit() is handled by the route or transaction manager
        return new_message
