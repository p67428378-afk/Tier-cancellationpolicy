from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import User, Booking, CancellationLog, CancellationPolicyRule, MembershipTier, BookingStatus
from payment_gateway import PaymentGateway

class CancellationService:
    def __init__(self, db_session: Session, payment_gateway: PaymentGateway):
        self.db_session = db_session
        self.payment_gateway = payment_gateway

    def calculate_refund_percentage(self, membership_tier: MembershipTier, days_before_check_in: float) -> float:
        """Calculates the refund percentage based on membership tier and days before check-in."""
        rule = self.db_session.query(CancellationPolicyRule).filter(
            CancellationPolicyRule.membership_tier == membership_tier,
            CancellationPolicyRule.min_days_before_check_in <= days_before_check_in,
            CancellationPolicyRule.max_days_before_check_in >= days_before_check_in
        ).first()

        if rule:
            return rule.refund_percentage
        return 0.0  # Default to no refund if no rule matches

    def cancel_booking(self, user_id: str, booking_id: str, reason_for_cancellation: str = None):
        """Handles the cancellation of a booking and processes refunds."""
        user = self.db_session.query(User).filter_by(id=user_id).first()
        booking = self.db_session.query(Booking).filter_by(id=booking_id).first()

        if not user:
            return {"status": "failed", "message": "User not found", "errorCode": "USER_NOT_FOUND"}
        if not booking:
            return {"status": "failed", "message": "Booking not found", "errorCode": "BOOKING_NOT_FOUND"}
        if booking.booking_status == BookingStatus.CANCELLED:
            return {"status": "failed", "message": "Booking already cancelled", "errorCode": "BOOKING_ALREADY_CANCELLED"}

        cancellation_date_time = datetime.utcnow()
        time_difference: timedelta = booking.check_in_date_time - cancellation_date_time
        days_before_check_in = time_difference.total_seconds() / (24 * 3600)

        membership_tier = user.membership_tier
        refund_percentage = self.calculate_refund_percentage(membership_tier, days_before_check_in)
        refund_amount = booking.total_booking_amount * refund_percentage

        # Process refund via payment gateway
        payment_response = self.payment_gateway.process_refund(refund_amount, booking_id, user_id)
        refund_transaction_id = payment_response.get("transaction_id")

        if payment_response["status"] == "success":
            booking.booking_status = BookingStatus.CANCELLED
            self.db_session.add(booking)

            cancellation_log = CancellationLog(
                booking_id=booking_id,
                user_id=user_id,
                cancellation_date_time=cancellation_date_time,
                membership_tier_at_cancellation=membership_tier,
                days_before_check_in=days_before_check_in,
                refund_percentage_applied=refund_percentage,
                refund_amount=refund_amount,
                refund_transaction_id=refund_transaction_id
            )
            self.db_session.add(cancellation_log)
            self.db_session.commit()

            return {
                "cancellationStatus": "success",
                "refundAmount": round(refund_amount, 2),
                "refundTransactionId": refund_transaction_id,
                "membershipTierApplied": membership_tier.value
            }
        else:
            self.db_session.rollback()
            return {
                "cancellationStatus": "failed",
                "message": payment_response.get("message", "Payment gateway error"),
                "errorCode": "PAYMENT_GATEWAY_ERROR"
            }
