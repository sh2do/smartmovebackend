from flask import Blueprint, request, current_app
from app.services.mpesa_service import MpesaService
from app.utils.response import success, error_response as error
from app.models.booking import Booking, PaymentStatus # Import Booking and PaymentStatus
from app.extensions import db # Import db for database operations
from requests.exceptions import ConnectionError # Import ConnectionError
from app.utils.decorators import jwt_required # Import jwt_required
from ipaddress import ip_address, ip_network # New import for IP whitelisting
import os # New import for os.environ.get

payment_bp = Blueprint("payments", __name__)


@payment_bp.route("/stk-push", methods=["POST"])
@jwt_required
def initiate_payment(current_user): # current_user is passed by jwt_required
    data = request.get_json()
    phone = data.get("phone")
    amount = data.get("amount")
    booking_id = data.get("booking_id")

    if not all([phone, amount, booking_id]):
        return error("Missing required fields: phone, amount, booking_id", 400)

    # Authorization: Ensure the booking belongs to the current user
    booking = Booking.query.get(booking_id)
    if not booking:
        return error("Booking not found", 404)
    if booking.user_id != current_user.id:
        return error("Unauthorized: Booking does not belong to the current user.", 403)

    try:
        db.session.begin_nested() # Start a nested transaction
        # Trigger the prompt
        response = MpesaService.stk_push(phone, amount, booking_id)

        # Check if STK Push was successful (Mpesa's response code for successful initiation)
        if response.get("ResponseCode") == "0":
            booking.checkout_request_id = response.get("CheckoutRequestID")
            booking.payment_status = PaymentStatus.PENDING # Set payment status to pending
            db.session.add(booking) # Mark for addition to session (already loaded, but good practice)
            db.session.commit() # Commit the nested transaction
            return success(data=response, message="STK Push Initiated Successfully")
        else:
            db.session.rollback() # Rollback if Mpesa initiation failed
            # Log Mpesa specific error for internal debugging
            current_app.logger.error(f"Mpesa STK Push Initiation Failed: {response.get('ResponseDescription', 'N/A')} - {response.get('CustomerMessage', 'N/A')}")
            return error(response.get('CustomerMessage', "STK Push Initiation Failed"), status_code=400)

    except ConnectionError as e: # Catch errors from MpesaService
        db.session.rollback()
        current_app.logger.error(f"Failed to initiate Mpesa STK Push due to connection error: {e}")
        return error(f"Failed to connect to Mpesa: {e}", 500)
    except Exception as e:
        db.session.rollback() # Rollback any database changes if an unexpected error occurs
        current_app.logger.error(f"An unexpected error occurred during Mpesa STK Push initiation: {e}", exc_info=True)
        return error("An unexpected error occurred. Please try again.", 500)


@payment_bp.route("/callback", methods=["POST"])
def payment_callback():
    # --- Security: IP Whitelisting ---
    # M-Pesa's official callback IP ranges should be configured here.
    # Example: MPESA_CALLBACK_IPS = os.environ.get('MPESA_CALLBACK_IPS', '196.201.214.0/24,196.201.214.64/26').split(',')
    # It's crucial to get the official IP ranges from Safaricom/M-Pesa documentation.
    
    MPESA_CALLBACK_IP_RANGES_STR = os.environ.get('MPESA_CALLBACK_IPS', '127.0.0.1/32').split(',') # Default to localhost for dev
    MPESA_CALLBACK_IP_RANGES = [ip_network(ip_str) for ip_str in MPESA_CALLBACK_IP_RANGES_STR]

    client_ip = ip_address(request.remote_addr)
    is_whitelisted = False
    for network in MPESA_CALLBACK_IP_RANGES:
        if client_ip in network:
            is_whitelisted = True
            break
    
    if not is_whitelisted:
        current_app.logger.warning(f"Unauthorized callback attempt from IP: {client_ip}")
        return error("Unauthorized access to callback endpoint.", 403)
    # --- End Security ---

    # This is where M-Pesa sends the results (Success/Fail)
    data = request.get_json()

    # --- Security: Signature Verification (HIGH PRIORITY) ---
    # M-Pesa callbacks often include a signature or hash in headers or payload
    # to verify authenticity. This implementation is missing.
    # You MUST implement signature verification using M-Pesa's documentation
    # to prevent spoofed callback requests.
    signature_header = request.headers.get('X-Mpesa-Signature') # Example header
    if not signature_header:
        current_app.logger.warning("M-Pesa callback received without signature header. Possible spoofing attempt!")
        # For now, we'll process but log a warning. In production, this should likely return an error.
    # --- End Security ---
    
    
    # Extract relevant fields
    result_code = data["Body"]["stkCallback"]["ResultCode"]
    checkout_request_id = data["Body"]["stkCallback"]["CheckoutRequestID"]
    
    mpesa_receipt_number = None
    amount = None

    # CallbackMetadata might not be present for failed transactions
    callback_metadata_items = data["Body"]["stkCallback"].get("CallbackMetadata", {}).get("Item", [])
    
    for item in callback_metadata_items:
        if item["Name"] == "MpesaReceiptNumber":
            mpesa_receipt_number = item["Value"]
        elif item["Name"] == "Amount":
            amount = item["Value"]

    booking = Booking.query.filter_by(checkout_request_id=checkout_request_id).first()

    if booking:
        if result_code == 0: # Successful transaction (integer 0)
            booking.mpesa_receipt_number = mpesa_receipt_number
            booking.payment_status = PaymentStatus.COMPLETED
        else: # Failed or cancelled transaction
            booking.payment_status = PaymentStatus.FAILED
        db.session.commit()
    else:
        # Log an error if booking not found for a callback
        current_app.logger.error(f"Booking not found for CheckoutRequestID: {checkout_request_id}")

    return success(message="Callback processed")
