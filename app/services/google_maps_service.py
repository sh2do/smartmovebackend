import math
import requests
from flask import current_app


class GoogleMapsService:
    GOOGLE_MAPS_BASE_URL = "https://maps.googleapis.com/maps/api"

    @staticmethod
    def get_distance(lat1, lon1, lat2, lon2):
        """
        Calculate the great circle distance between two points
        on the earth (specified in decimal degrees)
        """
        # Convert decimal degrees to radians
        lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])

        # Haversine formula
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = (
            math.sin(dlat / 2) ** 2
            + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
        )
        c = 2 * math.asin(math.sqrt(a))

        # Radius of earth in kilometers is 6371
        km = 6371 * c
        return round(km, 2)

    @staticmethod
    def get_distance_matrix(origin, destination, mode="driving"):
        """
        Fetches distance and duration between an origin and destination using Google Distance Matrix API.
        Origin and destination can be addresses or lat/lng coordinates.
        """
        api_key = current_app.config.get('GOOGLE_MAPS_API_KEY')
        if not api_key:
            raise ValueError("Google Maps API Key is not configured.")

        endpoint = f"{GoogleMapsService.GOOGLE_MAPS_BASE_URL}/distancematrix/json"
        params = {
            "origins": origin,
            "destinations": destination,
            "mode": mode,
            "key": api_key,
        }

        try:
            response = requests.get(endpoint, params=params, timeout=5) # Add a timeout for external API call
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            data = response.json()

            if data["status"] == "OK" and data["rows"]:
                element = data["rows"][0]["elements"][0]
                if element["status"] == "OK":
                    return {
                        "distance": element["distance"]["value"],  # meters
                        "duration": element["duration"]["value"],  # seconds
                        "origin": origin,
                        "destination": destination,
                    }
                else:
                    raise ValueError(f"Google Maps API element status: {element['status']}")
            else:
                raise ValueError(f"Google Maps API status: {data['status']}")
        except requests.exceptions.Timeout:
            raise TimeoutError("Google Maps API request timed out.")
        except requests.exceptions.RequestException as e:
            raise ConnectionError(f"Error connecting to Google Maps API: {e}")
        except Exception as e:
            raise ValueError(f"Failed to get distance matrix: {e}")
