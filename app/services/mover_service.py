from app.extensions import db
from app.models.mover import Mover
from app.models.user import User

class MoverService:
    @staticmethod
    def update_mover_profile(mover_id: int, data: dict):
        mover = Mover.query.get(mover_id)
        if not mover:
            raise ValueError("Mover not found.")

        # Whitelist fields that can be updated
        allowed_fields = ['company_name', 'bio', 'service_area'] # Add other fields as per Mover model
        
        updated = False
        for key, value in data.items():
            if key in allowed_fields:
                setattr(mover, key, value)
                updated = True
            else:
                # Optionally log attempts to update disallowed fields
                # current_app.logger.warning(f"Attempted to update disallowed mover field: {key}")
                pass
        
        if updated:
            db.session.add(mover)
            # db.session.commit() is handled by the route
        
        return mover

    @staticmethod
    def get_availability(mover_id: int):
        mover = Mover.query.get(mover_id)
        if not mover:
            raise ValueError("Mover not found.")
        
        # Placeholder for real availability logic (e.g., checking a schedule table)
        return {"mover_id": mover_id, "status": "Available", "next_slot": "2026-03-15T09:00:00Z"}
