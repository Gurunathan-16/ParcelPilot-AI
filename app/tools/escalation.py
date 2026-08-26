import sqlite3
from datetime import datetime
from zoneinfo import ZoneInfo

from app.data.database import DATABASE_FILE


def prepare_escalation(
    ticket_id: str,
    account_id: str,
    priority: str,
    reason: str
):
    """
    Prepare an escalation.

    IMPORTANT:
    This function does NOT modify the database.
    It only prepares an action for user confirmation.
    """

    if priority not in {"P1", "P2", "P3"}:
        return {
            "success": False,
            "message": "Invalid priority."
        }

    connection = sqlite3.connect(DATABASE_FILE)
    connection.row_factory = sqlite3.Row

    try:
        cursor = connection.execute(
            """
            SELECT *
            FROM tickets
            WHERE ticket_id = ?
            AND account_id = ?
            """,
            (ticket_id, account_id)
        )

        ticket = cursor.fetchone()

        if not ticket:
            return {
                "success": False,
                "message": "Ticket not found for this account."
            }

        return {
            "success": True,
            "requires_confirmation": True,
            "action": "create_escalation",
            "ticket_id": ticket_id,
            "account_id": account_id,
            "priority": priority,
            "reason": reason,
            "message": (
                f"Escalation prepared for {ticket_id}. "
                "Explicit user confirmation is required."
            )
        }

    finally:
        connection.close()


def confirm_escalation(
    ticket_id: str,
    account_id: str,
    priority: str,
    reason: str,
    confirmed: bool,
    created_by: str = "support_agent"
):
    """
    Execute an escalation only after explicit confirmation.
    """

    if confirmed is not True:
        return {
            "success": False,
            "executed": False,
            "message": "Escalation was not confirmed."
        }

    connection = sqlite3.connect(DATABASE_FILE)

    try:
        # Verify ticket ownership again before changing state.
        cursor = connection.execute(
            """
            SELECT ticket_id
            FROM tickets
            WHERE ticket_id = ?
            AND account_id = ?
            """,
            (ticket_id, account_id)
        )

        ticket = cursor.fetchone()

        if not ticket:
            return {
                "success": False,
                "executed": False,
                "message": "Ticket not found for this account."
            }

        created_at = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).isoformat()

        cursor = connection.execute(
            """
            INSERT INTO escalations (
                ticket_id,
                account_id,
                priority,
                reason,
                status,
                created_at,
                created_by
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
            """,
            (
                ticket_id,
                account_id,
                priority,
                reason,
                "OPEN",
                created_at,
                created_by
            )
        )

        connection.commit()

        return {
            "success": True,
            "executed": True,
            "escalation_id": cursor.lastrowid,
            "ticket_id": ticket_id,
            "account_id": account_id,
            "priority": priority,
            "status": "OPEN",
            "created_at": created_at
        }

    finally:
        connection.close()