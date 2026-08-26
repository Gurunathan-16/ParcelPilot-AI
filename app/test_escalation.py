from app.tools.escalation import (
    prepare_escalation,
    confirm_escalation
)


print("\nPREPARE ESCALATION")
print("=" * 60)

prepared = prepare_escalation(
    ticket_id="TKT-001",
    account_id="ACCT-002",
    priority="P1",
    reason="Unauthorized access test."
)

print(prepared)


print("\nTRY WITHOUT CONFIRMATION")
print("=" * 60)

result = confirm_escalation(
    ticket_id="TKT-001",
    account_id="ACCT-001",
    priority="P1",
    reason="Customer issue requires urgent investigation.",
    confirmed=False
)

print(result)

print("\nCONFIRM ESCALATION")
print("=" * 60)

result = confirm_escalation(
    ticket_id="TKT-001",
    account_id="ACCT-001",
    priority="P1",
    reason="Customer issue requires urgent investigation.",
    confirmed=True
)

print(result)