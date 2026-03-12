import uuid
import time

class PaymentGateway:
    def __init__(self, api_key):
        self.api_key = api_key
        print(f"Payment Gateway initialized with API Key: {self.api_key}")

    def process_refund(self, amount, booking_id, user_id):
        """Simulates processing a refund."""
        print(f"Processing refund for booking {booking_id}, user {user_id} for amount {amount}")
        # Simulate network delay or processing time
        time.sleep(0.5)

        # Simulate success or failure based on some condition (e.g., amount)
        if amount < 0:
            print("Refund failed: Invalid amount.")
            return {"status": "failed", "transaction_id": None, "message": "Invalid amount"}
        elif amount == 0:
            print("Refund processed: Zero amount, no actual transaction.")
            return {"status": "success", "transaction_id": "NO_REFUND_NEEDED", "message": "Zero amount refund"}
        else:
            transaction_id = f"txn_{uuid.uuid4().hex}"
            print(f"Refund successful. Transaction ID: {transaction_id}")
            return {"status": "success", "transaction_id": transaction_id, "message": "Refund processed successfully"}

