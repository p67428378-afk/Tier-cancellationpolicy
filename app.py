from flask import Flask, request, jsonify
from config import Config
from database import Session, init_db
from models import User, Booking, MembershipTier, BookingStatus
from cancellation_service import CancellationService
from payment_gateway import PaymentGateway
from datetime import datetime, timedelta, UTC

app = Flask(__name__)
app.config.from_object(Config)

# Initialize DB and add some dummy data for testing
with app.app_context():
    init_db()
    db_session = Session()
    # Add dummy users if not present
    if not db_session.query(User).filter_by(id="user123").first():
        db_session.add(User(id="user123", membership_tier=MembershipTier.BRONZE))
        db_session.add(User(id="user456", membership_tier=MembershipTier.SILVER))
        db_session.add(User(id="user789", membership_tier=MembershipTier.GOLD))
        db_session.commit()
        print("Dummy users added.")

    # Add dummy bookings for testing
    if not db_session.query(Booking).filter_by(id="booking101").first():
        # Booking 1: Check-in 8 days from now (100% refund)
        db_session.add(Booking(id="booking101", user_id="user123", check_in_date_time=datetime.now(UTC) + timedelta(days=8), total_booking_amount=200.00, booking_status=BookingStatus.CONFIRMED))
        # Booking 2: Check-in 3 days from now (partial refund based on tier)
        db_session.add(Booking(id="booking102", user_id="user456", check_in_date_time=datetime.now(UTC) + timedelta(days=3), total_booking_amount=300.00, booking_status=BookingStatus.CONFIRMED))
        # Booking 3: Check-in 12 hours from now (less than 24h, partial/no refund)
        db_session.add(Booking(id="booking103", user_id="user789", check_in_date_time=datetime.now(UTC) + timedelta(hours=12), total_booking_amount=400.00, booking_status=BookingStatus.CONFIRMED))
        # Booking 4: Already cancelled
        db_session.add(Booking(id="booking104", user_id="user123", check_in_date_time=datetime.now(UTC) + timedelta(days=5), total_booking_amount=150.00, booking_status=BookingStatus.CANCELLED))
        # Booking 5: Check-in 2 hours ago (no-show/after check-in)
        db_session.add(Booking(id="booking105", user_id="user456", check_in_date_time=datetime.now(UTC) - timedelta(hours=2), total_booking_amount=250.00, booking_status=BookingStatus.CONFIRMED))
        db_session.commit()
        print("Dummy bookings added.")
    db_session.close()

# Initialize payment gateway and cancellation service
payment_gateway = PaymentGateway(api_key=app.config['PAYMENT_GATEWAY_API_KEY'])
cancellation_service = CancellationService(db_session=Session(), payment_gateway=payment_gateway)

@app.route('/api/v1/bookings/<string:booking_id>/cancel', methods=['POST'])
def cancel_booking(booking_id):
    data = request.get_json()
    user_id = data.get('userId')
    reason_for_cancellation = data.get('reasonForCancellation')

    if not user_id:
        return jsonify({"status": "failed", "message": "userId is required", "errorCode": "MISSING_USER_ID"}), 400

    result = cancellation_service.cancel_booking(user_id, booking_id, reason_for_cancellation)

    if result["status"] == "success": # Changed from cancellationStatus to status
        return jsonify(result), 200
    else:
        status_code = 500
        if result["errorCode"] in ["USER_NOT_FOUND", "BOOKING_NOT_FOUND", "BOOKING_ALREADY_CANCELLED"]:
            status_code = 404
        elif result["errorCode"] == "MISSING_USER_ID":
            status_code = 400
        return jsonify(result), status_code

if __name__ == '__main__':
    app.run(debug=True)
