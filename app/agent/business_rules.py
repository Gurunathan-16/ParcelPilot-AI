def determine_cancellation_rule(
    customer_name: str,
    order_status: str,
    pickup_actual_at,
    customer_agreement: dict | None
):
    """
    Determine whether cancellation is allowed
    and whether a fee applies.
    """

    # Already picked up
    if order_status == "PICKED_UP":
        return {
            "can_cancel": False,
            "fee_applies": None,
            "reason": (
                "Shipment has already been picked up. "
                "Standard return-to-origin process applies."
            )
        }

    # Northstar-specific agreement
    if (
        customer_name == "Northstar Logistics"
        and customer_agreement
    ):
        return {
            "can_cancel": True,
            "fee_applies": False,
            "reason": (
                "Northstar's active agreement allows "
                "BOOKED shipments to be cancelled before "
                "pickup without a cancellation fee."
            ),
            "source_priority": "customer_agreement"
        }

    # Default behavior
    return {
        "can_cancel": True,
        "fee_applies": None,
        "reason": (
            "Cancellation must be evaluated using the "
            "current ParcelPilot cancellation SOP."
        ),
        "source_priority": "current_sop"
    }