from app.tools.calculations import (
    calculate_delay_hours,
    calculate_default_service_credit
)


print("\nDELAY CALCULATION")
print("=" * 60)

delay = calculate_delay_hours(
    "2026-08-16T08:00:00",
    "2026-08-16T11:30:00"
)

print(delay)


print("\nSERVICE CREDIT")
print("=" * 60)

credit = calculate_default_service_credit(
    shipment_fee_inr=4000,
    delay_hours=3.5,
    carrier_fault=True,
    customer_fault=False
)

print(credit)