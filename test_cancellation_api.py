import pytest
from app import app, Session, init_db
from models import User, Booking, MembershipTier, BookingStatus
from datetime import datetime, timedelta, UTC

@pytest.fixture(scope='module')
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        with app.app_context():
            # Ensure a clean database for testing
            init_db() # Re-initialize to clear previous data
            db_session = Session()
            # Add test data
            db_session.add(User(id="test_user_bronze", membership_tier=MembershipTier.BRONZE))
            db_session.add(User(id="test_user_silver", membership_tier=MembershipTier.SILVER))
            db_session.add(User(id="test_user_gold", membership_tier=MembershipTier.GOLD))
            
            # Booking for 8 days from now (100% refund)
            db_session.add(Booking(id="test_booking_100_percent", user_id="test_user_gold", 
                                   check_in_date_time=datetime.now(UTC) + timedelta(days=8), 
                                   total_booking_amount=100.00, booking_status=BookingStatus.CONFIRMED))
            
            # Booking for 3 days from now (Silver, 75% refund)
            db_session.add(Booking(id="test_booking_75_percent", user_id="test_user_silver", 
                                   check_in_date_time=datetime.now(UTC) + timedelta(days=3), 
                                   total_booking_amount=100.00, booking_status=BookingStatus.CONFIRMED))
            
            # Booking for 12 hours from now (Gold, 50% refund)
            db_session.add(Booking(id="test_booking_50_percent", user_id="test_user_gold", 
                                   check_in_date_time=datetime.now(UTC) + timedelta(hours=12), 
                                   total_booking_amount=100.00, booking_status=BookingStatus.CONFIRMED))
            
            # Already cancelled booking
            db_session.add(Booking(id="test_booking_cancelled", user_id="test_user_bronze", 
                                   check_in_date_time=datetime.now(UTC) + timedelta(days=2), 
                                   total_booking_amount=100.00, booking_status=BookingStatus.CANCELLED))
            
            # Booking in the past (No-show, 0% refund)
            db_session.add(Booking(id="test_booking_no_show", user_id="test_user_bronze", 
                                   check_in_date_time=datetime.now(UTC) - timedelta(hours=1), 
                                   total_booking_amount=100.00, booking_status=BookingStatus.CONFIRMED))
            
            db_session.commit()
            db_session.close()
        yield client

def test_cancel_booking_100_percent_refund(client):
    response = client.post('/api/v1/bookings/test_booking_100_percent/cancel', json={
        'userId': 'test_user_gold',
        'reasonForCancellation': 'Test reason'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success' # Changed from cancellationStatus to status
    assert data['refundAmount'] == 100.00
    assert data['membershipTierApplied'] == 'Gold'

def test_cancel_booking_75_percent_refund(client):
    response = client.post('/api/v1/bookings/test_booking_75_percent/cancel', json={
        'userId': 'test_user_silver',
        'reasonForCancellation': 'Test reason'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success' # Changed from cancellationStatus to status
    assert data['refundAmount'] == 75.00
    assert data['membershipTierApplied'] == 'Silver'

def test_cancel_booking_50_percent_refund(client):
    response = client.post('/api/v1/bookings/test_booking_50_percent/cancel', json={
        'userId': 'test_user_gold',
        'reasonForCancellation': 'Test reason'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success' # Changed from cancellationStatus to status
    assert data['refundAmount'] == 50.00
    assert data['membershipTierApplied'] == 'Gold'

def test_cancel_booking_already_cancelled(client):
    response = client.post('/api/v1/bookings/test_booking_cancelled/cancel', json={
        'userId': 'test_user_bronze',
        'reasonForCancellation': 'Test reason'
    })
    assert response.status_code == 404 # Or 400 depending on desired error handling
    data = response.get_json()
    assert data['status'] == 'failed' # Changed from cancellationStatus to status
    assert data['errorCode'] == 'BOOKING_ALREADY_CANCELLED'

def test_cancel_booking_not_found(client):
    response = client.post('/api/v1/bookings/non_existent_booking/cancel', json={
        'userId': 'test_user_bronze',
        'reasonForCancellation': 'Test reason'
    })
    assert response.status_code == 404
    data = response.get_json()
    assert data['status'] == 'failed' # Changed from cancellationStatus to status
    assert data['errorCode'] == 'BOOKING_NOT_FOUND'

def test_cancel_booking_user_not_found(client):
    response = client.post('/api/v1/bookings/test_booking_100_percent/cancel', json={
        'userId': 'non_existent_user',
        'reasonForCancellation': 'Test reason'
    })
    assert response.status_code == 404
    data = response.get_json()
    assert data['status'] == 'failed' # Changed from cancellationStatus to status
    assert data['errorCode'] == 'USER_NOT_FOUND'

def test_cancel_booking_missing_user_id(client):
    response = client.post('/api/v1/bookings/test_booking_100_percent/cancel', json={
        'reasonForCancellation': 'Test reason'
    })
    assert response.status_code == 400
    data = response.get_json()
    assert data['status'] == 'failed' # Changed from cancellationStatus to status
    assert data['errorCode'] == 'MISSING_USER_ID'

def test_cancel_booking_no_show(client):
    response = client.post('/api/v1/bookings/test_booking_no_show/cancel', json={
        'userId': 'test_user_bronze',
        'reasonForCancellation': 'Test reason'
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data['status'] == 'success' # Changed from cancellationStatus to status
    assert data['refundAmount'] == 0.00
    assert data['membershipTierApplied'] == 'Bronze'
