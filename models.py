from sqlalchemy import Column, Integer, String, DateTime, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class MembershipTier(enum.Enum):
    BRONZE = "Bronze"
    SILVER = "Silver"
    GOLD = "Gold"

class BookingStatus(enum.Enum):
    CONFIRMED = "Confirmed"
    CANCELLED = "Cancelled"
    NOSHOW = "NoShow"

class User(Base):
    __tablename__ = 'users'
    id = Column(String, primary_key=True)
    membership_tier = Column(Enum(MembershipTier), nullable=False, default=MembershipTier.BRONZE)

    def __repr__(self):
        return f"<User(id='{self.id}', membership_tier='{self.membership_tier.value}')>"

class Booking(Base):
    __tablename__ = 'bookings'
    id = Column(String, primary_key=True)
    user_id = Column(String, nullable=False)
    check_in_date_time = Column(DateTime, nullable=False)
    booking_status = Column(Enum(BookingStatus), nullable=False, default=BookingStatus.CONFIRMED)
    total_booking_amount = Column(Float, nullable=False)

    def __repr__(self):
        return f"<Booking(id='{self.id}', user_id='{self.user_id}', status='{self.booking_status.value}')>"

class CancellationLog(Base):
    __tablename__ = 'cancellation_logs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    booking_id = Column(String, nullable=False)
    user_id = Column(String, nullable=False)
    cancellation_date_time = Column(DateTime, nullable=False, default=datetime.utcnow)
    membership_tier_at_cancellation = Column(Enum(MembershipTier), nullable=False)
    days_before_check_in = Column(Float, nullable=False)
    refund_percentage_applied = Column(Float, nullable=False)
    refund_amount = Column(Float, nullable=False)
    refund_transaction_id = Column(String, nullable=True)

    def __repr__(self):
        return f"<CancellationLog(booking_id='{self.booking_id}', refund_amount={self.refund_amount})>"

class CancellationPolicyRule(Base):
    __tablename__ = 'cancellation_policy_rules'
    id = Column(Integer, primary_key=True, autoincrement=True)
    membership_tier = Column(Enum(MembershipTier), nullable=False)
    min_days_before_check_in = Column(Float, nullable=False)
    max_days_before_check_in = Column(Float, nullable=False)
    refund_percentage = Column(Float, nullable=False)

    def __repr__(self):
        return f"<CancellationPolicyRule(tier='{self.membership_tier.value}', min_days={self.min_days_before_check_in}, max_days={self.max_days_before_check_in}, refund={self.refund_percentage})>"
