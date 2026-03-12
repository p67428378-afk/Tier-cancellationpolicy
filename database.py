from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from models import Base, MembershipTier, CancellationPolicyRule, User, Booking, CancellationLog # Import models

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
