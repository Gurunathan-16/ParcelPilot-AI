class AuthorizationError(Exception):
    """
    Raised when a user is not authorized to access
    a customer account.
    """
    pass


# ============================================================
# ACCESS CHECK
# ============================================================

def can_access_account(
    user: dict,
    account_id: str
) -> bool:
    """
    Determine whether the current user can access
    the requested customer account.
    """

    if not user:
        return False

    role = user.get("role")

    # --------------------------------------------------------
    # Internal ParcelPilot users
    # --------------------------------------------------------

    if role in {
        "support",
        "operations",
        "admin"
    }:
        return True

    # --------------------------------------------------------
    # Customer users
    # --------------------------------------------------------

    if role == "customer":
        return user.get("account_id") == account_id

    # --------------------------------------------------------
    # Unknown role
    # --------------------------------------------------------

    return False


# ============================================================
# REQUIRE ACCESS
# ============================================================

def require_account_access(
    user: dict,
    account_id: str
):
    """
    Raise AuthorizationError when the user does not
    have access to the requested account.
    """

    if not can_access_account(
        user,
        account_id
    ):
        raise AuthorizationError(
            f"Access denied for account {account_id}."
        )

    return True

class AuthorizationError(Exception):
    """Raised when a user is not authorized."""
    pass


def can_access_account(user: dict, account_id: str) -> bool:
    role = user.get("role")

    if role in {"support", "operations", "admin"}:
        return True

    if role == "customer":
        return user.get("account_id") == account_id

    return False


def require_account_access(user: dict, account_id: str):
    if not can_access_account(user, account_id):
        raise AuthorizationError(
            f"Access denied for account {account_id}."
        )

    return True