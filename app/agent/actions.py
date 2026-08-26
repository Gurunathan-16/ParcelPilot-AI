import sqlite3

from app.data.database import DATABASE_FILE
from app.security.access_control import require_account_access

def create_escalation(
    account_id: str,
    reason: str,
    ticket_id: str = None
):
    """
    Create a support escalation.

    This function ensures the escalations table exists with
    TEXT-compatible IDs so SQLite does not produce datatype mismatch.
    """

    conn = sqlite3.connect(DATABASE_FILE)

    try:
        cursor = conn.cursor()

        # ---------------------------------------------------------
        # Ensure escalation table exists
        # ---------------------------------------------------------

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS escalations (
                escalation_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                ticket_id TEXT,
                reason TEXT NOT NULL
            )
            """
        )

        # ---------------------------------------------------------
        # Get next escalation number safely
        # ---------------------------------------------------------

        cursor.execute(
            """
            SELECT escalation_id
            FROM escalations
            WHERE escalation_id LIKE 'ESC-%'
            ORDER BY rowid DESC
            LIMIT 1
            """
        )

        row = cursor.fetchone()

        if row and row[0]:
            try:
                last_number = int(row[0].replace("ESC-", ""))
                next_number = last_number + 1
            except (ValueError, AttributeError):
                next_number = 1
        else:
            next_number = 1

        escalation_id = f"ESC-{next_number:04d}"

        # ---------------------------------------------------------
        # Insert escalation
        # ---------------------------------------------------------

        cursor.execute(
            """
            INSERT INTO escalations
            (
                escalation_id,
                account_id,
                ticket_id,
                reason
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                str(escalation_id),
                str(account_id),
                ticket_id,
                str(reason)
            )
        )

        conn.commit()

        return {
            "success": True,
            "message": "Escalation created successfully.",
            "escalation": {
                "escalation_id": escalation_id,
                "account_id": account_id,
                "ticket_id": ticket_id,
                "reason": reason
            }
        }

    except Exception as error:

        conn.rollback()

        return {
            "success": False,
            "message": str(error)
        }

    finally:
        conn.close()


def cancel_order(account_id: str, order_id: str):
    """
    Cancel an order after explicit user confirmation.
    """

    conn = sqlite3.connect(DATABASE_FILE)

    try:
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT status
            FROM orders
            WHERE order_id = ?
            AND account_id = ?
            """,
            (
                order_id,
                account_id
            )
        )

        row = cursor.fetchone()

        if not row:
            return {
                "success": False,
                "message": "Order not found."
            }

        current_status = row[0]

        if current_status != "BOOKED":
            return {
                "success": False,
                "message": (
                    f"Order {order_id} cannot be cancelled "
                    f"because its current status is "
                    f"{current_status}."
                )
            }

        cursor.execute(
            """
            UPDATE orders
            SET status = 'CANCELLED'
            WHERE order_id = ?
            AND account_id = ?
            """,
            (
                order_id,
                account_id
            )
        )

        conn.commit()

        return {
            "success": True,
            "message": (
                f"Order {order_id} cancelled successfully."
            ),
            "order_id": order_id,
            "account_id": account_id,
            "status": "CANCELLED"
        }

    except Exception as error:

        conn.rollback()

        return {
            "success": False,
            "message": str(error)
        }

    finally:
        conn.close()