from sqlalchemy import create_engine, Column, Integer, String, DateTime, Float, Enum
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime
import enum

# Define the base for declarative models
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

# Database setup
DATABASE_URL = 'sqlite:///cancellation_policy.db'
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)
    print("Database initialized and tables created.")

    # Add default cancellation policy rules if not present
    session = Session()
    if session.query(CancellationPolicyRule).count() == 0:
        print("Adding default cancellation policy rules...")
        rules = [
            # 7 Days or More: 100% refund for all tiers
            CancellationPolicyRule(membership_tier=MembershipTier.BRONZE, min_days_before_check_in=7.0, max_days_before_check_in=float('inf'), refund_percentage=1.00),
            CancellationPolicyRule(membership_tier=MembershipTier.SILVER, min_days_before_check_in=7.0, max_days_before_check_in=float('inf'), refund_percentage=1.00),
            CancellationPolicyRule(membership_tier=MembershipTier.GOLD, min_days_before_check_in=7.0, max_days_before_check_in=float('inf'), refund_percentage=1.00),

            # Between 1 and 6 Days
            CancellationPolicyRule(membership_tier=MembershipTier.BRONZE, min_days_before_check_in=1.0, max_days_before_check_in=6.999, refund_percentage=0.50),
            CancellationPolicyRule(membership_tier=MembershipTier.SILVER, min_days_before_check_in=1.0, max_days_before_check_in=6.999, refund_percentage=0.75),
            CancellationPolicyRule(membership_tier=MembershipTier.GOLD, min_days_before_check_in=1.0, max_days_before_check_in=6.999, refund_percentage=0.90),

            # Less than 24 Hours (0 to 0.999 days)
            CancellationPolicyRule(membership_tier=MembershipTier.BRONZE, min_days_before_check_in=0.0, max_days_before_check_in=0.999, refund_percentage=0.00),
            CancellationPolicyRule(membership_tier=MembershipTier.SILVER, min_days_before_check_in=0.0, max_days_before_check_in=0.999, refund_percentage=0.25),
            CancellationPolicyRule(membership_tier=MembershipTier.GOLD, min_days_before_check_in=0.0, max_days_before_check_in=0.999, refund_percentage=0.50),

            # After Check-in Time / No-Show
            CancellationPolicyRule(membership_tier=MembershipTier.BRONZE, min_days_before_check_in=float('-inf'), max_days_before_check_in=-0.001, refund_percentage=0.00),
            CancellationPolicyRule(membership_tier=MembershipTier.SILVER, min_days_before_check_in=float('-inf'), max_days_before_check_in=-0.001, refund_percentage=0.00),
            CancellationPolicyRule(membership_tier=MembershipTier.GOLD, min_days_before_check_in=float('-inf'), max_days_before_check_in=-0.001, refund_percentage=0.00),
        ]
        session.add_all(rules)
        session.commit()
        print("Default rules added.")
    session.close()

if __name__ == '__main__':
    init_db()

