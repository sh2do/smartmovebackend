import requests
import base64
from datetime import datetime
from flask import current_app
from requests.auth import HTTPBasicAuth


class MpesaService:
    @staticmethod
    def get_token():
        url = f"{current_app.config['MPESA_BASE_URL']}/oauth/v1/generate?grant_type=client_credentials"
        try:
            resp = requests.get(
                url,
                auth=HTTPBasicAuth(
                    current_app.config["MPESA_CONSUMER_KEY"],
                    current_app.config["MPESA_CONSUMER_SECRET"],
                ),
                timeout=10 # Added timeout
            )
            resp.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            token = resp.json().get("access_token")
            if not token:
                current_app.logger.error(f"Mpesa get_token response missing access_token: {resp.text}")
                raise ValueError("Mpesa API did not return an access token.")
            return token
        except requests.exceptions.Timeout:
            current_app.logger.error("Mpesa get_token request timed out.")
            raise ConnectionError("Mpesa API token request timed out.")
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Mpesa get_token request failed: {e}, Response: {getattr(e.response, 'text', 'N/A')}")
            raise ConnectionError(f"Error connecting to Mpesa API for token: {e}")
        except ValueError as e:
            raise # Re-raise if token missing
        except Exception as e:
            current_app.logger.error(f"An unexpected error occurred in Mpesa get_token: {e}")
            raise ConnectionError(f"Unexpected error in Mpesa token retrieval: {e}")

    @staticmethod
    def stk_push(phone, amount, booking_id):
        token = MpesaService.get_token()
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        password_string = f"{current_app.config['MPESA_SHORTCODE']}{current_app.config['MPESA_PASSKEY']}{timestamp}"
        password = base64.b64encode(password_string.encode()).decode()

        payload = {
            "BusinessShortCode": current_app.config["MPESA_SHORTCODE"],
            "Password": password,
            "Timestamp": timestamp,
            "TransactionType": "CustomerPayBillOnline",
            "Amount": amount,
            "PartyA": phone,
            "PartyB": current_app.config["MPESA_SHORTCODE"],
            "PhoneNumber": phone,
            "CallBackURL": current_app.config["CALLBACK_URL"],
            "AccountReference": f"SMOVE-{booking_id}",
            "TransactionDesc": "Payment for Smartmove",
        }

        headers = {"Authorization": f"Bearer {token}"}
        
        try:
            response = requests.post(
                f"{current_app.config['MPESA_BASE_URL']}/mpesa/stkpush/v1/processrequest",
                json=payload,
                headers=headers,
                timeout=15 # Added timeout
            )
            response.raise_for_status() # Raise an HTTPError for bad responses (4xx or 5xx)
            return response.json()
        except requests.exceptions.Timeout:
            current_app.logger.error("Mpesa stk_push request timed out.")
            raise ConnectionError("Mpesa API STK Push request timed out.")
        except requests.exceptions.RequestException as e:
            current_app.logger.error(f"Mpesa stk_push request failed: {e}, Payload: {payload}, Response: {getattr(e.response, 'text', 'N/A')}")
            raise ConnectionError(f"Error connecting to Mpesa API for STK Push: {e}")
        except Exception as e:
            current_app.logger.error(f"An unexpected error occurred in Mpesa stk_push: {e}, Payload: {payload}")
            raise ConnectionError(f"Unexpected error in Mpesa STK Push: {e}")
