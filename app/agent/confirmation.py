CONFIRMATION_WORDS = {
    "yes",
    "y",
    "proceed",
    "confirm",
    "confirmed",
    "go ahead",
    "yes proceed",
    "yes, proceed",
}


REJECTION_WORDS = {
    "no",
    "n",
    "cancel",
    "stop",
    "don't",
    "do not",
    "no thanks",
}


def is_confirmation(message: str) -> bool:

    if not message:
        return False

    return (
        message.strip()
        .lower()
        in CONFIRMATION_WORDS
    )


def is_rejection(message: str) -> bool:

    if not message:
        return False

    return (
        message.strip()
        .lower()
        in REJECTION_WORDS
    )