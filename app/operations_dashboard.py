import streamlit as st
import pandas as pd
from pathlib import Path


st.set_page_config(
    page_title="ParcelPilot Operations",
    page_icon="📊",
    layout="wide"
)

st.title("📊 ParcelPilot Operations Dashboard")
st.caption("Internal support and operations view")


# Find Excel file
possible_files = [
    Path("ParcelPilot_Assessment_Data.xlsx"),
    Path("data/ParcelPilot_Assessment_Data.xlsx"),
    Path("app/data/ParcelPilot_Assessment_Data.xlsx"),
]

excel_file = next((p for p in possible_files if p.exists()), None)

if not excel_file:
    st.error("ParcelPilot_Assessment_Data.xlsx not found.")
    st.stop()


# Load workbook
excel = pd.ExcelFile(excel_file)

st.sidebar.header("Data")

st.sidebar.write("Available sheets:")
st.sidebar.write(excel.sheet_names)


# Load sheets
data = {}

for sheet in excel.sheet_names:
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet)
        data[sheet] = df
    except Exception:
        pass


# Find useful tables
tickets = None
orders = None
accounts = None

for name, df in data.items():

    columns = [str(c).lower() for c in df.columns]

    if "ticket" in name.lower() or any("ticket" in c for c in columns):
        if tickets is None:
            tickets = df

    if "order" in name.lower() or any("order" in c for c in columns):
        if orders is None:
            orders = df

    if "account" in name.lower() or any("account" in c for c in columns):
        if accounts is None:
            accounts = df


# Metrics
col1, col2, col3, col4 = st.columns(4)

if tickets is not None:
    col1.metric("Total Tickets", len(tickets))
else:
    col1.metric("Total Tickets", "N/A")

if orders is not None:
    col2.metric("Total Orders", len(orders))
else:
    col2.metric("Total Orders", "N/A")

if accounts is not None:
    col3.metric("Accounts", len(accounts))
else:
    col3.metric("Accounts", "N/A")

col4.metric("Status", "Operational")


st.divider()


# Ticket analysis
if tickets is not None:

    st.subheader("🎫 Support Activity")

    st.dataframe(
        tickets,
        use_container_width=True,
        height=350
    )

    # Look for severity
    severity_column = next(
        (
            c for c in tickets.columns
            if str(c).lower() in ["severity", "priority", "priority_level"]
        ),
        None
    )

    if severity_column:

        st.subheader("🚨 Ticket Priority")

        counts = tickets[severity_column].value_counts()

        st.bar_chart(counts)


    # Look for category/type
    category_column = next(
        (
            c for c in tickets.columns
            if str(c).lower() in ["category", "issue_type", "type", "topic"]
        ),
        None
    )

    if category_column:

        st.subheader("📈 Recurring Issues")

        counts = tickets[category_column].value_counts()

        st.bar_chart(counts.head(10))


# Orders
if orders is not None:

    st.subheader("📦 Orders")

    st.dataframe(
        orders,
        use_container_width=True,
        height=300
    )


# Accounts
if accounts is not None:

    st.subheader("🏢 Accounts")

    st.dataframe(
        accounts,
        use_container_width=True,
        height=300
    )


st.divider()

st.info(
    "This dashboard provides authorised support users with a "
    "high-level view of support activity, recurring issues, and "
    "operational data."
)