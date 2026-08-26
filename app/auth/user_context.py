from dataclasses import dataclass
from fastapi import Header, HTTPException


@dataclass
class UserContext:
    user_id: str
    role: str
    account_id: str | None = None


DEMO_USERS = {
    "support": UserContext(
        user_id="USR-001",
        role="support",
        account_id=None,
    ),
    "northstar": UserContext(
        user_id="USR-002",
        role="customer",
        account_id="ACCT-001",
    ),
    "lumenworks": UserContext(
        user_id="USR-003",
        role="customer",
        account_id="ACCT-002",
    ),
}


def get_current_user(
    x_user: str = Header(default="support")
) -> UserContext:

    user = DEMO_USERS.get(x_user.lower())

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid demo user."
        )

    return user


def get_demo_user() -> UserContext:
    return DEMO_USERS["support"]