from app.agent.confirmation import is_confirmation


def test_confirmation():
    test_messages = [
        "Yes",
        "yes",
        "Proceed",
        "Go ahead",
        "Maybe",
        "No",
        "I am not sure"
    ]

    print("\nCONFIRMATION TEST")
    print("=" * 50)

    for message in test_messages:
        result = is_confirmation(message)

        status = "✅ CONFIRMED" if result else "❌ NOT CONFIRMED"

        print(f"{message:20} → {status}")


if __name__ == "__main__":
    test_confirmation()