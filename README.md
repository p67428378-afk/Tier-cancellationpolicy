# Tiered Cancellation & Refund Policy Implementation

This repository contains the implementation for a tiered cancellation and refund policy based on customer membership level and time before check-in.

## Features

- **Membership Tier Recognition**: Identifies customer membership tier (Bronze, Silver, Gold).
- **Cancellation Window Calculation**: Calculates the time difference between cancellation request and check-in.
- **Tiered Refund Application**: Applies refund percentages based on membership tier and cancellation window.
- **API Endpoint**: Provides a dedicated API for handling cancellation requests.
- **Database Integration**: Stores user, booking, cancellation log, and policy rules.
- **Payment Gateway Integration**: Mocks integration with a payment gateway for refund processing.

## Technical Stack

- Python 3.9+
- Flask (for API)
- SQLAlchemy (for ORM and database interactions)
- SQLite (for local development database)

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/p67428378-afk/Tier-cancellationpolicy.git
    cd Tier-cancellationpolicy
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Initialize the database:**
    ```bash
    python database.py
    ```

5.  **Run the Flask application:**
    ```bash
    python app.py
    ```

    The API will be available at `http://127.0.0.1:5000`.

## API Endpoint

### `POST /api/v1/bookings/{bookingId}/cancel`

Handles cancellation requests, validates eligibility, calculates refunds, and triggers payment gateway interactions.

**Request Body Example:**

```json
{
  "userId": "user123",
  "bookingId": "booking456",
  "reasonForCancellation": "Change of plans"
}
```

**Response Example (Success):**

```json
{
  "cancellationStatus": "success",
  "refundAmount": 75.00,
  "refundTransactionId": "txn_789012345",
  "membershipTierApplied": "Silver"
}
```

**Response Example (Error):**

```json
{
  "cancellationStatus": "failed",
  "message": "Booking not found",
  "errorCode": "BOOKING_NOT_FOUND"
}
```

## Database Schema

-   **User Table**: `id`, `membership_tier` (Bronze, Silver, Gold)
-   **Booking Table**: `id`, `user_id`, `check_in_date_time`, `booking_status`, `total_booking_amount`
-   **Cancellation_Log Table**: `id`, `booking_id`, `user_id`, `cancellation_date_time`, `membership_tier_at_cancellation`, `days_before_check_in`, `refund_percentage_applied`, `refund_amount`, `refund_transaction_id`
-   **Cancellation_Policy_Rules Table**: `id`, `membership_tier`, `min_days_before_check_in`, `max_days_before_check_in`, `refund_percentage`

## Configuration

See `config.py` for database and other settings.
