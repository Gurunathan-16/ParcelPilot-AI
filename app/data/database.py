import sqlite3

from pathlib import Path


# ============================================================
# PATHS
# ============================================================

EXCEL_FILE = Path(
    "data/ParcelPilot_Assessment_Data.xlsx"
)

DATABASE_FILE = Path(
    "data/parcelpilot.db"
)


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():

    return sqlite3.connect(
        DATABASE_FILE
    )


# ============================================================
# INITIALIZE DATABASE
# ============================================================

def initialize_database():

    import pandas as pd

    connection = get_connection()

    try:

        # ----------------------------------------------------
        # Load Excel
        # ----------------------------------------------------

        accounts = pd.read_excel(
            EXCEL_FILE,
            sheet_name="accounts"
        )

        orders = pd.read_excel(
            EXCEL_FILE,
            sheet_name="orders"
        )

        tickets = pd.read_excel(
            EXCEL_FILE,
            sheet_name="tickets"
        )

        # ----------------------------------------------------
        # Accounts
        # ----------------------------------------------------

        accounts.to_sql(
            "accounts",
            connection,
            if_exists="replace",
            index=False
        )

        # ----------------------------------------------------
        # Orders
        # ----------------------------------------------------

        orders.to_sql(
            "orders",
            connection,
            if_exists="replace",
            index=False
        )

        # ----------------------------------------------------
        # Tickets
        # ----------------------------------------------------

        tickets.to_sql(
            "tickets",
            connection,
            if_exists="replace",
            index=False
        )

        # ----------------------------------------------------
        # Escalations
        # ----------------------------------------------------

        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS escalations (
                escalation_id TEXT PRIMARY KEY,
                account_id TEXT NOT NULL,
                ticket_id TEXT,
                reason TEXT NOT NULL
            )
            """
        )

        connection.commit()

        print(
            "✅ Database initialized successfully."
        )

        print(
            f"Accounts: {len(accounts)}"
        )

        print(
            f"Orders: {len(orders)}"
        )

        print(
            f"Tickets: {len(tickets)}"
        )

        print(
            "Escalations table: READY"
        )

    finally:

        connection.close()


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    initialize_database()