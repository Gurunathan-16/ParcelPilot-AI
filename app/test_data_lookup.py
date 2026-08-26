from app.tools.data_lookup import (
    get_account,
    get_order,
    get_ticket
)


print("\nACCOUNT")
print("=" * 60)

account = get_account("ACCT-001")
print(account)


print("\nORDER")
print("=" * 60)

order = get_order(
    "ORD-1001",
    "ACCT-001"
)

print(order)


print("\nTICKET")
print("=" * 60)

ticket = get_ticket(
    "TKT-001",
    "ACCT-001"
)

print(ticket)

print("\nSECURITY TEST")
print("=" * 60)

# Intentionally try to access an order
# using the WRONG account.

unauthorized_order = get_order(
    "ORD-1001",
    "ACCT-002"
)

print(unauthorized_order)