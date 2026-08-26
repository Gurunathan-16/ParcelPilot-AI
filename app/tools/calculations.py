from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


REFERENCE_TIME = datetime(
    2026,
    8,
    16,
    11,
    0,
    tzinfo=ZoneInfo("Asia/Kolkata")
)


def parse_datetime(value):
    """Convert a dataset datetime string into a timezone-aware datetime."""

    if not value:
        return None

    if isinstance(value, datetime):
        if value.tzinfo is None:
            return value.replace(
                tzinfo=ZoneInfo("Asia/Kolkata")
            )
        return value

    value = str(value).strip()

    # Handle Excel-style timestamps
    dt = datetime.fromisoformat(
        value.replace("Z", "+00:00")
    )

    if dt.tzinfo is None:
        dt = dt.replace(
            tzinfo=ZoneInfo("Asia/Kolkata")
        )

    return dt


def hours_between(start, end):
    """Calculate elapsed hours between two timestamps."""

    start = parse_datetime(start)
    end = parse_datetime(end)

    if not start or not end:
        return None

    return round(
        (end - start).total_seconds() / 3600,
        2
    )


def calculate_delay_hours(
    pickup_window_end,
    pickup_actual_at
):
    """
    Calculate how many hours late a pickup was.
    """

    pickup_window_end = parse_datetime(
        pickup_window_end
    )

    pickup_actual_at = parse_datetime(
        pickup_actual_at
    )

    if not pickup_window_end or not pickup_actual_at:
        return {
            "calculated": False,
            "reason": "Missing pickup timing data."
        }

    delay_hours = (
        pickup_actual_at - pickup_window_end
    ).total_seconds() / 3600

    return {
        "calculated": True,
        "delay_hours": round(max(delay_hours, 0), 2)
    }


def calculate_default_service_credit(
    shipment_fee_inr,
    delay_hours,
    carrier_fault,
    customer_fault
):
    """
    Apply the default ParcelPilot failed-pickup credit rule.

    Default rule:
    - More than 2 hours late
    - Carrier at fault
    - Customer not at fault
    - Credit = lower of INR 500 or 10% of shipment fee
    """

    if carrier_fault is None or customer_fault is None:
        return {
            "eligible": False,
            "reason": "Fault information is unknown."
        }

    if carrier_fault is not True:
        return {
            "eligible": False,
            "reason": "Carrier fault is not established."
        }

    if customer_fault is True:
        return {
            "eligible": False,
            "reason": "Customer fault is established."
        }

    if delay_hours is None:
        return {
            "eligible": False,
            "reason": "Pickup delay is unknown."
        }

    if delay_hours <= 2:
        return {
            "eligible": False,
            "reason": "Delay does not exceed the 2-hour threshold."
        }

    credit = min(
        500,
        shipment_fee_inr * 0.10
    )

    return {
        "eligible": True,
        "credit_inr": round(credit, 2),
        "approval_required": credit > 1000
    }