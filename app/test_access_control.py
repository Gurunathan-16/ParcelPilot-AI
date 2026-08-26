from app.security.access_control import (
    can_access_account,
    require_account_access,
    AuthorizationError,
)


customer = {
    "user_id": "user-001",
    "role": "customer",
    "account_id": "ACCT-001",
}

support_user = {
    "user_id": "support-001",
    "role": "support",
}


print("=" * 60)
print("ACCESS CONTROL TEST")
print("=" * 60)


# Customer accessing own account
print(
    "Customer → ACCT-001:",
    can_access_account(customer, "ACCT-001")
)


# Customer accessing another account
print(
    "Customer → ACCT-002:",
    can_access_account(customer, "ACCT-002")
)


# Support accessing customer account
print(
    "Support → ACCT-002:",
    can_access_account(support_user, "ACCT-002")
)


# Test enforcement
try:
    require_account_access(
        customer,
        "ACCT-002"
    )

    print("❌ Security failure")

except AuthorizationError as error:
    print("✅ Access correctly denied")
    print(error)