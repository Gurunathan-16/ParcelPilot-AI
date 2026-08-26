import sqlite3

from app.data.database import DATABASE_FILE


def initialize_escalation_table():
    connection = sqlite3.connect(DATABASE_FILE)

    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS escalations (
                escalation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticket_id TEXT NOT NULL,
                account_id TEXT NOT NULL,
                priority TEXT NOT NULL,
                reason TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                created_by TEXT NOT NULL
            )
            """
        )

        connection.commit()

        print("Escalation table initialized.")

    finally:
        connection.close()


if __name__ == "__main__":
    initialize_escalation_table()