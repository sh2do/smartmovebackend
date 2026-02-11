from flask import Blueprint, request, current_app
from app.utils.response import success, error_response
from app.services.google_maps_service import GoogleMapsService
from app.utils.validators import validate_request

maps_bp = Blueprint('maps', __name__)

@maps_bp.route('/calculate-distance', methods=['POST'])
@validate_request('origin', 'destination')
def calculate_distance():
    """
    Calculates the distance between two points using Google Maps API.
    """
    data = request.get_json()
    origin = data['origin']
    destination = data['destination']
    
    try:
        distance_info = GoogleMapsService.get_distance_matrix(origin, destination)
        return success(distance_info)
    except Exception as e:
        return error_response(str(e), 500)

@maps_bp.route('/config/google-maps-key', methods=['GET'])
def get_google_maps_api_key():
    """
    Returns the Google Maps API key for frontend usage.
    """
    api_key = current_app.config.get('GOOGLE_MAPS_API_KEY')
    if not api_key:
        return error_response("Google Maps API key not configured on the backend.", 500)
    return success({'googleMapsApiKey': api_key})

