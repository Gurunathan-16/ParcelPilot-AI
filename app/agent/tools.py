from app.data.vector_store import search_documents

from app.agent.actions import create_escalation

from app.tools.data_lookup import (
    find_account_by_name,
    get_account,
    get_order,
    get_ticket,
)
from app.security.access_control import require_account_access

# ============================================================
# ACCOUNT
# ============================================================

def lookup_account(account_name: str):
    """
    Find an account by customer name.
    """

    return find_account_by_name(account_name)


def lookup_account_by_id(account_id: str):
    """
    Find an account by account ID.
    """

    return get_account(account_id)


# ============================================================
# ORDER
# ============================================================

def lookup_order(
    order_id: str,
    account_id: str
):
    """
    Look up an order belonging to a specific account.
    """

    return get_order(
        order_id=order_id,
        account_id=account_id
    )


# ============================================================
# TICKET
# ============================================================

def lookup_ticket(
    ticket_id: str,
    account_id: str
):
    """
    Look up a ticket belonging to a specific account.
    """

    return get_ticket(
        ticket_id=ticket_id,
        account_id=account_id
    )


# ============================================================
# DOCUMENT SEARCH
# ============================================================

def search_documents_tool(query: str):
    """
    Search policies, SOPs, agreements and documentation.
    """

    return search_documents(query)


# ============================================================
# ESCALATION
# ============================================================

def create_escalation_tool(
    account_id: str,
    reason: str,
    ticket_id: str = None
):
    """
    Create an escalation after confirmation.
    """

    return create_escalation(
        account_id=account_id,
        reason=reason,
        ticket_id=ticket_id
    )