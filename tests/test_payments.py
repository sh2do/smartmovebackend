# tests/test_payments.py
import pytest
from unittest.mock import patch, MagicMock
from app import create_app
from app.extensions import db
from app.models.booking import Booking, PaymentStatus
from app.models.user import User
from app.models.mover import Mover
from app.models.address import Address
from app.services.mpesa_service import MpesaService
from datetime import datetime




@pytest.fixture
def auth_headers(client, sample_user): # Use sample_user fixture
    with client.application.app_context():
        print(f"DEBUG: sample_user in auth_headers: {sample_user}")
        retrieved_user_in_fixture = User.query.get(sample_user.id)
        print(f"DEBUG: retrieved_user_in_fixture: {retrieved_user_in_fixture}")
        assert retrieved_user_in_fixture is not None # Ensure user is found here
        # Log in the sample user to get a real token
        login_data = {
            'email': sample_user.email,
            'password': 'password123' # Use the password used to create sample_user
        }
        response = client.post('/api/auth/login', json=login_data)
        assert response.status_code == 200
        token = response.json['data']['token']
        return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def setup_booking(init_database):
    user = User(email='booking@example.com')
    user.set_password('password')
    mover_user = User(email='mover@example.com')
    mover_user.set_password('password')
    mover = Mover(user=mover_user)
    pickup_address = Address(
        street='123 Pickup St', city='Nairobi', state='Nairobi', zip_code='00100'
    )
    dropoff_address = Address(
        street='456 Dropoff Ave', city='Nairobi', state='Nairobi', zip_code='00100'
    )
    
    db.session.add_all([user, mover, pickup_address, dropoff_address])
    db.session.commit()

    booking = Booking(
        user_id=user.id,
        mover_id=mover.id,
        pickup_address_id=pickup_address.id,
        dropoff_address_id=dropoff_address.id,
        booking_time=datetime.fromisoformat('2024-12-25T10:00:00'),
        amount=100.00,
        payment_status=PaymentStatus.PENDING
    )
    db.session.add(booking)
    db.session.commit()
    return booking


# --- MpesaService Tests ---

@patch('app.services.mpesa_service.requests.get')
def test_get_token_success(mock_get, client): # Add client fixture
    with client.application.app_context(): # Wrap in app context
        mock_get.return_value.json.return_value = {'access_token': 'test_token'}
        token = MpesaService.get_token()
        assert token == 'test_token'

@patch('app.services.mpesa_service.requests.get')
def test_get_token_failure(mock_get, client): # Add client fixture
    with client.application.app_context(): # Wrap in app context
        mock_get.return_value.json.return_value = {'error': 'failed'}
        with pytest.raises(ValueError, match="Mpesa API did not return an access token."):
            MpesaService.get_token()

@patch('app.services.mpesa_service.requests.post')
@patch('app.services.mpesa_service.MpesaService.get_token', return_value='test_token')
def test_stk_push_success(mock_get_token, mock_post, client): # Add client fixture
    with client.application.app_context(): # Wrap in app context
        mock_post.return_value.json.return_value = {
            'ResponseCode': '0',
            'CheckoutRequestID': 'ws_CO_270720201010101010',
            'CustomerMessage': 'Success. Request accepted for processing'
        }
        response = MpesaService.stk_push('254712345678', 100, 1)
        assert response['ResponseCode'] == '0'
        assert 'CheckoutRequestID' in response

@patch('app.services.mpesa_service.requests.post')
@patch('app.services.mpesa_service.MpesaService.get_token', return_value='test_token')
def test_stk_push_failure(mock_get_token, mock_post, client): # Add client fixture
    with client.application.app_context(): # Wrap in app context
        mock_post.return_value.json.return_value = {
            'ResponseCode': '1',
            'CustomerMessage': 'Failure. Invalid Request'
        }
        response = MpesaService.stk_push('254712345678', 100, 1)
        assert response['ResponseCode'] == '1'
        assert 'CheckoutRequestID' not in response


# --- Payment Routes Tests ---

@patch('app.routes.payments.MpesaService.stk_push')
def test_initiate_payment_success(mock_stk_push, client, auth_headers, setup_booking):
    mock_stk_push.return_value = {
        'ResponseCode': '0',
        'CheckoutRequestID': 'ws_CO_270720201010101010',
        'CustomerMessage': 'Success. Request accepted for processing'
    }
    
    booking = setup_booking
    with client.application.app_context():
        response = client.post('/api/payments/stk-push', json={
            'phone': '254712345678',
            'amount': 100.00,
            'booking_id': booking.id
        }, headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json['message'] == 'STK Push Initiated Successfully'
    
    updated_booking = Booking.query.get(booking.id)
    assert updated_booking.checkout_request_id == 'ws_CO_270720201010101010'
    assert updated_booking.payment_status == PaymentStatus.PENDING

@patch('app.routes.payments.MpesaService.stk_push')
def test_initiate_payment_missing_fields(mock_stk_push, client, auth_headers):
    with client.application.app_context():
        response = client.post('/api/payments/stk-push', json={
            'phone': '254712345678',
            'amount': 100.00
            # Missing booking_id
        }, headers=auth_headers)
    
    assert response.status_code == 400
    assert response.json['message'] == 'Missing required fields: phone, amount, booking_id'


@patch('app.routes.payments.MpesaService.stk_push')
def test_initiate_payment_booking_not_found(mock_stk_push, client, auth_headers):
    with client.application.app_context():
        response = client.post('/api/payments/stk-push', json={
            'phone': '254712345678',
            'amount': 100.00,
            'booking_id': 999 # Non-existent booking ID
        }, headers=auth_headers)
    
    assert response.status_code == 404
    assert response.json['message'] == 'Booking not found'


@patch('app.routes.payments.MpesaService.stk_push')
def test_initiate_payment_stk_push_failure(mock_stk_push, client, auth_headers, setup_booking):
    mock_stk_push.return_value = {
        'ResponseCode': '1',
        'CustomerMessage': 'Failure. Invalid Request'
    }
    
    booking = setup_booking
    with client.application.app_context():
        response = client.post('/api/payments/stk-push', json={
            'phone': '254712345678',
            'amount': 100.00,
            'booking_id': booking.id
        }, headers=auth_headers)
    
    assert response.status_code == 400
    assert response.json['message'] == 'STK Push Initiation Failed'
    
    updated_booking = Booking.query.get(booking.id)
    assert updated_booking.checkout_request_id is None # Should not be updated on failure
    assert updated_booking.payment_status == PaymentStatus.PENDING # Should remain pending


def test_payment_callback_success(client, setup_booking):
    booking = setup_booking
    booking.checkout_request_id = 'ws_CO_270720201010101010'
    db.session.commit()

    callback_data = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "11985-78326-1",
                "CheckoutRequestID": "ws_CO_270720201010101010",
                "ResultCode": 0,
                "ResultDesc": "The service request is processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "Amount", "Value": 100.00},
                        {"Name": "MpesaReceiptNumber", "Value": "RTP123ABCD"},
                        {"Name": "TransactionDate", "Value": 20200727101010},
                        {"Name": "PhoneNumber", "Value": 254712345678}
                    ]
                }
            }
        }
    }
    
    with client.application.app_context():
        response = client.post('/api/payments/callback', json=callback_data)
    
    assert response.status_code == 200
    assert response.json['message'] == 'Callback processed'
    
    updated_booking = Booking.query.get(booking.id)
    assert updated_booking.payment_status == PaymentStatus.COMPLETED
    assert updated_booking.mpesa_receipt_number == 'RTP123ABCD'


def test_payment_callback_failure(client, setup_booking):
    booking = setup_booking
    booking.checkout_request_id = 'ws_CO_270720201010101010_fail'
    db.session.commit()

    callback_data = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "11985-78326-1",
                "CheckoutRequestID": "ws_CO_270720201010101010_fail",
                "ResultCode": 1032, # Example failed ResultCode
                "ResultDesc": "Transaction cancelled by user"
            }
        }
    }
    
    with client.application.app_context():
        response = client.post('/api/payments/callback', json=callback_data)
    
    assert response.status_code == 200
    assert response.json['message'] == 'Callback processed'
    
    updated_booking = Booking.query.get(booking.id)
    assert updated_booking.payment_status == PaymentStatus.FAILED
    assert updated_booking.mpesa_receipt_number is None

def test_payment_callback_booking_not_found(client):
    callback_data = {
        "Body": {
            "stkCallback": {
                "MerchantRequestID": "11985-78326-1",
                "CheckoutRequestID": "non_existent_checkout_id", # No matching booking
                "ResultCode": 0,
                "ResultDesc": "The service request is processed successfully.",
                "CallbackMetadata": {
                    "Item": [
                        {"Name": "Amount", "Value": 100.00},
                        {"Name": "MpesaReceiptNumber", "Value": "RTP123ABCD"},
                        {"Name": "TransactionDate", "Value": 20200727101010},
                        {"Name": "PhoneNumber", "Value": 254712345678}
                    ]
                }
            }
        }
    }
    
    with client.application.app_context():
        response = client.post('/api/payments/callback', json=callback_data)
    
    assert response.status_code == 200
    assert response.json['message'] == 'Callback processed'
    # No booking should be updated, and no error should be returned to M-Pesa.
    # An error would be logged internally, but the external response should still be 200.