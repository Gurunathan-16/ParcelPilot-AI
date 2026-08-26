import sqlite3

from app.data.database import DATABASE_FILE


# ============================================================
# ACCOUNT LOOKUP
# ============================================================

def find_account_by_name(account_name: str):
    """
    Find a customer account by exact case-insensitive name.
    """

    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.execute(
            """
            SELECT *
            FROM accounts
            WHERE LOWER(TRIM(account_name)) = LOWER(TRIM(?))
            """,
            (account_name,)
        )

        row = cursor.fetchone()

        if not row:
            return {
                "found": False,
                "message": f"Account '{account_name}' not found."
            }

        return {
            "found": True,
            "data": dict(row)
        }

    finally:
        connection.close()


# ============================================================
# ACCOUNT BY ID
# ============================================================

def get_account(account_id: str):
    """
    Retrieve an account by account ID.
    """

    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.execute(
            """
            SELECT *
            FROM accounts
            WHERE account_id = ?
            """,
            (account_id,)
        )

        row = cursor.fetchone()

        if not row:
            return {
                "found": False,
                "message": "Account not found."
            }

        return {
            "found": True,
            "data": dict(row)
        }

    finally:
        connection.close()


# ============================================================
# ORDER LOOKUP
# ============================================================

def get_order(order_id: str, account_id: str):
    """
    Retrieve an order ONLY when it belongs to the
    specified customer account.

    Account ID is mandatory for security.
    """

    if not account_id:
        return {
            "found": False,
            "message": "Account ID is required to access an order."
        }

    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.execute(
            """
            SELECT *
            FROM orders
            WHERE order_id = ?
            AND account_id = ?
            """,
            (order_id, account_id)
        )

        row = cursor.fetchone()

        if not row:
            return {
                "found": False,
                "message": "Order not found for this account."
            }

        return {
            "found": True,
            "data": dict(row)
        }

    finally:
        connection.close()


# ============================================================
# TICKET LOOKUP
# ============================================================

def get_ticket(ticket_id: str, account_id: str):
    """
    Retrieve a ticket ONLY when it belongs to the
    specified customer account.

    Account ID is mandatory.

    This prevents cross-account data exposure.
    """

    if not account_id:
        return {
            "found": False,
            "message": "Account ID is required to access a ticket."
        }

    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.execute(
            """
            SELECT
                ticket_id,
                account_id,
                created_at,
                status,
                subject,
                description,
                channel,
                assigned_to,
                last_customer_message_at,
                historical_resolution
            FROM tickets
            WHERE ticket_id = ?
            AND account_id = ?
            """,
            (ticket_id, account_id)
        )

        row = cursor.fetchone()

        if not row:
            return {
                "found": False,
                "message": "Ticket not found for this account."
            }

        return {
            "found": True,
            "data": dict(row)
        }

    finally:
        connection.close()