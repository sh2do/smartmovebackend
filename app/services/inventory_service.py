from app.extensions import db
from app.models.inventory import Inventory
from app.models.user import User
from app.models.booking import Booking

class InventoryService:
    @staticmethod
    def get_user_inventory(current_user: User):
        """
        Retrieves all inventory items associated with a user's bookings.
        """
        # This assumes Inventory items are directly linked to bookings, and bookings to users.
        # This will need N+1 fix to be applied if not already.
        user_bookings = Booking.query.filter_by(user_id=current_user.id).all()
        inventory_items = []
        for booking in user_bookings:
            inventory_items.extend(booking.inventory_items) # assuming backref 'inventory_items' on Booking
        return inventory_items
        
    @staticmethod
    def add_inventory_item(current_user: User, data):
        """
        Adds a new item to a user's inventory, linked via a booking.
        Expects 'booking_id', 'name', 'quantity', 'description' (optional).
        """
        booking_id = data.get('booking_id')
        name = data.get('name')
        quantity = data.get('quantity')
        description = data.get('description')

        if not all([booking_id, name, quantity is not None]):
            raise ValueError("Booking ID, name, and quantity are required.")
        
        booking = Booking.query.get(booking_id)
        if not booking:
            raise ValueError("Booking not found.")
        
        # Authorization: Ensure the booking belongs to the current user
        if booking.user_id != current_user.id:
            raise ValueError("Unauthorized to add inventory to this booking.")

        new_item = Inventory(
            booking_id=booking_id,
            name=name,
            description=description,
            quantity=quantity
        )
        db.session.add(new_item)
        # db.session.commit() is handled by the route

        return new_item

    # Keeping these methods as placeholders for now if not used by routes directly
    @staticmethod
    def get_item(item_id):
        print(f"Retrieving inventory item with ID: {item_id}")
        return Inventory.query.get(item_id) # Actual DB query

    @staticmethod
    def update_item_quantity(item_id, quantity_change):
        print(f"Updating quantity for item {item_id} by {quantity_change}")
        item = Inventory.query.get(item_id)
        if not item:
            raise ValueError("Inventory item not found.")
        item.quantity += quantity_change
        db.session.add(item)
        return item

    @staticmethod
    def delete_item(item_id):
        print(f"Deleting inventory item with ID: {item_id}")
        item = Inventory.query.get(item_id)
        if not item:
            raise ValueError("Inventory item not found.")
        db.session.delete(item)
        return {"message": f"Item {item_id} deleted successfully"}
