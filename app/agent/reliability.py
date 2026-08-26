from typing import List, Dict, Any


# Higher number = higher authority
SOURCE_PRIORITY = {
    "customer_agreement": 100,
    "sop": 85,
    "general_policy": 80,
    "product_documentation": 70,
    "structured_data": 60,
    "historical_ticket": 20,
    "deprecated_policy": 10,
}


def get_source_priority(source: Dict[str, Any]) -> int:
    """
    Return the authority priority of a source.
    """

    source_type = source.get("source_type")

    return SOURCE_PRIORITY.get(source_type, 0)


def is_authoritative(source: Dict[str, Any]) -> bool:
    """
    Determine whether a source can be treated as authoritative.
    """

    status = source.get("status")

    # Deprecated documents are not authoritative.
    if status == "deprecated":
        return False

    # Historical ticket resolutions are context only.
    if source.get("source_type") == "historical_ticket":
        return False

    return True


def rank_sources(
    sources: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Remove non-authoritative sources and rank
    remaining sources by authority.
    """

    valid_sources = [
        source
        for source in sources
        if is_authoritative(source)
    ]

    return sorted(
        valid_sources,
        key=get_source_priority,
        reverse=True
    )


def find_customer_agreement(
    sources: List[Dict[str, Any]],
    customer_name: str
):
    """
    Find an active customer-specific agreement.
    """

    agreements = [
        source
        for source in sources
        if (
            source.get("source_type") == "customer_agreement"
            and source.get("customer") == customer_name
            and source.get("status") == "current"
        )
    ]

    return agreements


def detect_conflict(
    sources: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Detect whether retrieved sources may contain
    conflicting business rules.

    This is a source-level conflict detector.
    The actual business-rule comparison will happen
    later in the reasoning layer.
    """

    authoritative = [
        source
        for source in sources
        if is_authoritative(source)
    ]

    source_types = {
        source.get("source_type")
        for source in authoritative
    }

    has_customer_agreement = (
        "customer_agreement" in source_types
    )

    has_general_rule = (
        "sop" in source_types
        or "general_policy" in source_types
    )

    if has_customer_agreement and has_general_rule:
        return {
            "conflict_detected": True,
            "conflict_possible": True,
            "reason": (
                "A customer-specific agreement and a "
                "general policy/SOP were both retrieved. "
                "The customer agreement must be checked "
                "for applicable overrides."
            )
        }

    return {
        "conflict_detected": False,
        "conflict_possible": False,
        "reason": (
            "No obvious authority-level conflict was detected."
        )
    }


def evaluate_evidence(
    sources: List[Dict[str, Any]],
    customer_name: str = None
) -> Dict[str, Any]:
    """
    Evaluate retrieved evidence and determine
    whether the agent has sufficient authoritative evidence.
    """

    ranked_sources = rank_sources(sources)

    if not ranked_sources:
        return {
            "can_answer": False,
            "confidence": "low",
            "reason": "No authoritative sources found.",
            "sources": []
        }

    agreements = []

    if customer_name:
        agreements = find_customer_agreement(
            ranked_sources,
            customer_name
        )

    conflict = detect_conflict(ranked_sources)

    if agreements:
        return {
            "can_answer": True,
            "confidence": "high",
            "reason": (
                "An active customer-specific agreement "
                "was found. It should be checked before "
                "applying general policy."
            ),
            "customer_agreement": agreements[0],
            "conflict": conflict,
            "sources": ranked_sources
        }

    return {
        "can_answer": True,
        "confidence": "medium",
        "reason": (
            "Authoritative general sources were found, "
            "but no customer-specific agreement was retrieved."
        ),
        "customer_agreement": None,
        "conflict": conflict,
        "sources": ranked_sources
    }