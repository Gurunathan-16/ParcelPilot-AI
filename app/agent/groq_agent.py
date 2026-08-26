import os
import json
import re

from dotenv import load_dotenv
from groq import Groq

from app.agent.tools import (
    lookup_account,
    lookup_order,
    lookup_ticket,
    search_documents_tool,
)

from app.agent.actions import (
    create_escalation,
    cancel_order,
)

from app.agent.confirmation import is_confirmation

from app.api.session_manager import (
    get_pending_action,
    set_pending_action,
    clear_pending_action,
)

# ============================================================
# GLOBAL STATE
# ============================================================

pending_action = None


# ============================================================
# ENVIRONMENT
# ============================================================

load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not configured.")

client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# SYSTEM INSTRUCTION
# ============================================================

SYSTEM_INSTRUCTION = """
You are ParcelPilot AI Support Agent.

You help users answer questions about ParcelPilot
accounts, orders, tickets, policies, agreements,
and operational issues.

IMPORTANT SECURITY RULES:

1. Never invent data.

2. Use lookup_account when the user asks about an account.

3. Use lookup_order when the user asks about an order.

4. Use lookup_ticket when the user asks about a ticket.

5. Use search_documents when the question involves:
   - policies
   - SOPs
   - agreements
   - cancellation
   - service credits
   - SLAs
   - support terms
   - product documentation

6. Never expose another customer's data.

7. An order belongs to the account returned by the database.

8. A ticket belongs to the account returned by the database.

9. Never assume that a ticket belongs to an account supplied
   by the user.

10. If a user specifies both a ticket and account, the ticket
    must belong to that account.

11. If the ticket belongs to another account, do not expose
    ticket details.

12. Never escalate a ticket for an account different from the
    ticket's actual account.

13. Never execute a state-changing action without explicit
    confirmation.

14. "Yes", "Proceed", "Confirm", and "Go ahead" are valid
    confirmations.

15. "No", "Maybe", "Not sure", and ambiguous responses are
    not confirmation.

16. Never cancel an order merely because policy says it is
    eligible. The user must explicitly confirm.

17. Never create an escalation merely because the user
    mentioned an issue. Ask for confirmation first.

18. After creating an escalation, provide the escalation ID.

19. Customer-specific agreements may override general policies.

20. Current policies and SOPs are authoritative over historical
    ticket resolutions.

21. Historical ticket resolutions are context only.

22. Database results represent current operational state.

23. Retrieved documents represent policy, SOP, and agreement
    authority.

24. Never invent cancellation fees, procedures, deadlines,
    approval requirements, or other operational rules.

25. If information is insufficient, clearly say so.

26. Never ask for an account again if the account was already
    successfully identified in the current request.

27. When a user requests escalation of a ticket, verify:
    ticket -> account relationship before proceeding.

28. Never use a user-provided account name to override the
    ticket's actual account.

29. For cross-account requests, refuse access instead of
    revealing the ticket's details.
"""


# ============================================================
# TOOL DEFINITIONS
# ============================================================

TOOLS = [

    {
        "type": "function",
        "function": {
            "name": "lookup_account",
            "description": (
                "Find a ParcelPilot customer account by exact "
                "or near-exact customer name."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {
                        "type": "string",
                        "description": "Customer account name."
                    }
                },
                "required": ["account_name"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "lookup_order",
            "description": (
                "Look up an order. If the user specifies an "
                "account, always provide account_id."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string",
                        "description": "ParcelPilot order ID."
                    },
                    "account_id": {
                        "type": "string",
                        "description": "Customer account ID."
                    }
                },
                "required": [
                    "order_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "lookup_ticket",
            "description": (
                "Look up a support ticket. If the user specifies "
                "an account, account_id MUST also be provided. "
                "Never omit account_id when the user names an account."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string",
                        "description": "ParcelPilot ticket ID."
                    },
                    "account_id": {
                        "type": "string",
                        "description": (
                            "Customer account ID. Required when "
                            "the user specifies an account."
                        )
                    }
                },
                "required": [
                    "ticket_id"
                ]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": (
                "Search ParcelPilot policies, SOPs, agreements, "
                "and product documentation."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Precise search query."
                    }
                },
                "required": ["query"]
            }
        }
    },

    {
        "type": "function",
        "function": {
            "name": "create_escalation",
            "description": (
                "Create an escalation only after the user has "
                "explicitly confirmed."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "account_id": {
                        "type": "string"
                    },
                    "reason": {
                        "type": "string"
                    },
                    "ticket_id": {
                        "type": "string"
                    }
                },
                "required": [
                    "account_id",
                    "reason"
                ]
            }
        }
    }
]


# ============================================================
# ACCOUNT NAME -> ACCOUNT ID
# ============================================================

def resolve_account(account_name):

    result = lookup_account(account_name)

    if not result.get("found"):
        return None

    return result["data"]


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_tool(function_name, arguments):

    print(f"\n🔧 Tool selected: {function_name}")
    print(f"Arguments: {arguments}")

    # --------------------------------------------------------
    # ACCOUNT
    # --------------------------------------------------------

    if function_name == "lookup_account":

        result = lookup_account(
            account_name=arguments["account_name"]
        )

    # --------------------------------------------------------
    # ORDER
    # --------------------------------------------------------

    elif function_name == "lookup_order":

        result = lookup_order(
            order_id=arguments["order_id"],
            account_id=arguments.get("account_id")
        )

    # --------------------------------------------------------
    # TICKET
    # --------------------------------------------------------

    elif function_name == "lookup_ticket":

        result = lookup_ticket(
            ticket_id=arguments["ticket_id"],
            account_id=arguments.get("account_id")
        )

    # --------------------------------------------------------
    # DOCUMENT SEARCH
    # --------------------------------------------------------

    elif function_name == "search_documents":

        result = search_documents_tool(
            query=arguments["query"]
        )

    # --------------------------------------------------------
    # ESCALATION
    # --------------------------------------------------------

    elif function_name == "create_escalation":

        result = create_escalation(
            account_id=arguments["account_id"],
            reason=arguments["reason"],
            ticket_id=arguments.get("ticket_id")
        )

    else:

        result = {
            "error": f"Unknown tool: {function_name}"
        }

    print(f"Tool result: {result}")

    return result


# ============================================================
# EXPLICIT TICKET SECURITY CHECK
# ============================================================

def secure_ticket_lookup(ticket_id, requested_account_id=None):

    """
    Security wrapper around ticket lookup.

    If requested_account_id is supplied, the ticket must belong
    to that account.
    """

    result = lookup_ticket(
        ticket_id=ticket_id,
        account_id=requested_account_id
    )

    return result


# ============================================================
# PREPARE ESCALATION
# ============================================================

def prepare_escalation(
    account_id,
    account_name,
    reason,
    ticket_id=None
):

    global pending_action

    pending_action = {
        "action": "create_escalation",
        "account_id": account_id,
        "account_name": account_name,
        "reason": reason,
        "ticket_id": ticket_id,
    }

    message = (
        f"I found the account **{account_name}**.\n\n"
        f"**Account ID:** {account_id}\n\n"
        f"**Escalation reason:** {reason}\n\n"
    )

    if ticket_id:
        message += (
            f"**Ticket:** {ticket_id}\n\n"
        )

    message += (
        "Would you like me to create the escalation?\n\n"
        "Please reply **Yes** or **No**."
    )

    return message


# ============================================================
# HANDLE PENDING ACTION
# ============================================================

def handle_pending_action(user_message):

    global pending_action

    if not pending_action:
        return None

    action = pending_action["action"]

    # ========================================================
    # ESCALATION
    # ========================================================

    if action == "create_escalation":

        if is_confirmation(user_message):

            account_id = pending_action["account_id"]
            account_name = pending_action["account_name"]
            reason = pending_action["reason"]
            ticket_id = pending_action.get("ticket_id")

            # ------------------------------------------------
            # FINAL SECURITY CHECK FOR TICKET ESCALATION
            # ------------------------------------------------

            if ticket_id:

                ticket_result = secure_ticket_lookup(
                    ticket_id=ticket_id,
                    requested_account_id=account_id
                )

                if not ticket_result.get("found"):

                    pending_action = None

                    return (
                        "❌ I could not create the escalation "
                        "because the ticket could not be verified "
                        "for this account."
                    )

            print(
                "\n🔧 Tool selected: create_escalation"
            )

            print(
                "Arguments: "
                f"{{'account_id': '{account_id}', "
                f"'reason': '{reason}', "
                f"'ticket_id': '{ticket_id}'}}"
            )

            result = create_escalation(
                account_id=account_id,
                reason=reason,
                ticket_id=ticket_id
            )

            print(f"Tool result: {result}")

            pending_action = None

            if result.get("success"):

                escalation = result["escalation"]

                response = (
                    "✅ Escalation created successfully.\n\n"
                    f"**Escalation ID:** "
                    f"{escalation['escalation_id']}\n"
                    f"**Account:** {account_name}\n"
                    f"**Account ID:** {account_id}\n"
                )

                if ticket_id:
                    response += (
                        f"**Ticket:** {ticket_id}\n"
                    )

                response += (
                    f"**Reason:** {reason}"
                )

                return response

            return (
                "❌ I could not create the escalation.\n\n"
                f"{result.get('message', 'Unknown error.')}"
            )

        if user_message.strip().lower() in {
            "no",
            "n",
            "cancel",
            "don't",
            "do not"
        }:

            pending_action = None

            return (
                "Understood. I won't create the escalation."
            )

        return (
            "Please confirm the escalation by replying "
            "**Yes** or **No**."
        )

    # ========================================================
    # CANCELLATION
    # ========================================================

    if action == "cancel_order":

        if is_confirmation(user_message):

            account_id = pending_action["account_id"]
            order_id = pending_action["order_id"]

            print(
                "\n🔧 Tool selected: cancel_order"
            )

            print(
                f"Arguments: {{'account_id': '{account_id}', "
                f"'order_id': '{order_id}'}}"
            )

            result = cancel_order(
                account_id=account_id,
                order_id=order_id
            )

            print(f"Tool result: {result}")

            pending_action = None

            if result.get("success"):

                return (
                    f"✅ Order **{order_id}** has been "
                    f"successfully cancelled.\n\n"
                    f"**Account:** {account_id}\n"
                    f"**Status:** CANCELLED"
                )

            return (
                f"❌ I could not cancel order "
                f"**{order_id}**.\n\n"
                f"{result.get('message', 'Unknown error.')}"
            )

        if user_message.strip().lower() in {
            "no",
            "n",
            "cancel",
            "don't",
            "do not"
        }:

            order_id = pending_action["order_id"]

            pending_action = None

            return (
                f"Understood. I will not cancel "
                f"order **{order_id}**."
            )

        return (
            "Please confirm the cancellation by replying "
            "**Yes** or **No**."
        )

    return None


# ============================================================
# DETECT ACCOUNT NAME
# ============================================================

def extract_account_name(message):

    known_accounts = [
        "Northstar Logistics",
        "LumenWorks",
    ]

    message_lower = message.lower()

    for account in known_accounts:

        if account.lower() in message_lower:
            return account

    return None


# ============================================================
# DETECT TICKET ID
# ============================================================

def extract_ticket_id(message):

    match = re.search(
        r"\bTKT-\d+\b",
        message,
        re.IGNORECASE
    )

    if match:
        return match.group(0).upper()

    return None


# ============================================================
# DETECT ORDER ID
# ============================================================

def extract_order_id(message):

    match = re.search(
        r"\bORD-\d+\b",
        message,
        re.IGNORECASE
    )

    if match:
        return match.group(0).upper()

    return None


# ============================================================
# HANDLE ESCALATION REQUEST
# ============================================================

def handle_escalation_request(user_message):

    ticket_id = extract_ticket_id(user_message)
    account_name = extract_account_name(user_message)

    message_lower = user_message.lower()

    is_escalation = (
        "escalate" in message_lower
        or "escalation" in message_lower
        or "human support" in message_lower
    )

    if not is_escalation:
        return None

    # ========================================================
    # TICKET ESCALATION
    # ========================================================

    if ticket_id:

        # ----------------------------------------------------
        # If account is explicitly supplied, resolve it first.
        # ----------------------------------------------------

        requested_account = None

        if account_name:

            requested_account = resolve_account(
                account_name
            )

            if not requested_account:

                return (
                    f"I couldn't find the account "
                    f"**{account_name}**."
                )

        requested_account_id = None

        if requested_account:
            requested_account_id = (
                requested_account["account_id"]
            )

        # ----------------------------------------------------
        # If account was supplied, enforce ticket ownership.
        # ----------------------------------------------------

        ticket_result = secure_ticket_lookup(
            ticket_id=ticket_id,
            requested_account_id=requested_account_id
        )

        if not ticket_result.get("found"):

            if requested_account_id:

                return (
                    f"I can't access ticket **{ticket_id}** "
                    f"for **{account_name}** because the ticket "
                    f"is not associated with that account."
                )

            return (
                f"I couldn't find ticket **{ticket_id}**."
            )

        ticket = ticket_result["data"]

        actual_account_id = ticket["account_id"]

        actual_account = resolve_account(
            actual_account_id
        )

        if not actual_account:

            return (
                "I found the ticket, but I couldn't verify "
                "its customer account."
            )

        actual_account_name = actual_account["account_name"]

        # ----------------------------------------------------
        # IMPORTANT SECURITY CHECK
        # ----------------------------------------------------

        if (
            requested_account_id
            and requested_account_id != actual_account_id
        ):

            return (
                f"I can't escalate ticket **{ticket_id}** "
                f"for **{account_name}** because the ticket "
                "is not associated with that account."
            )

        reason = (
            f"{ticket['subject']}: "
            f"{ticket['description']}"
        )

        return prepare_escalation(
            account_id=actual_account_id,
            account_name=actual_account_name,
            reason=reason,
            ticket_id=ticket_id
        )

    # ========================================================
    # ACCOUNT-LEVEL ESCALATION
    # ========================================================

    if account_name:

        account = resolve_account(
            account_name
        )

        if not account:

            return (
                f"I couldn't find the account "
                f"**{account_name}**."
            )

        # ----------------------------------------------------
        # Extract actual reason.
        # ----------------------------------------------------

        reason = user_message

        # Remove account name from generic reason.
        reason = re.sub(
            re.escape(account_name),
            "",
            reason,
            flags=re.IGNORECASE
        ).strip()

        if not reason:

            return (
                f"I found **{account_name}** "
                f"(Account ID: **{account['account_id']}**).\n\n"
                "What issue would you like me to escalate?"
            )

        return prepare_escalation(
            account_id=account["account_id"],
            account_name=account["account_name"],
            reason=reason
        )

    return (
        "I can help create an escalation, but I need "
        "the customer account or ticket ID first."
    )


# ============================================================
# HANDLE CANCELLATION REQUEST
# ============================================================

def handle_cancellation_request(user_message):

    order_id = extract_order_id(user_message)

    if not order_id:
        return None

    if "cancel" not in user_message.lower():
        return None

    account_name = extract_account_name(
        user_message
    )

    if not account_name:

        global pending_action

        pending_action = {
            "action": "awaiting_cancel_account",
            "order_id": order_id,
        }

        return (
            f"I can help cancel order **{order_id}**.\n\n"
            "Please provide the customer account name "
            f"associated with **{order_id}**."
        )

    account = resolve_account(
        account_name
    )

    if not account:

        return (
            f"I couldn't find the account "
            f"**{account_name}**."
        )

    order_result = lookup_order(
        order_id=order_id,
        account_id=account["account_id"]
    )

    if not order_result.get("found"):

        return (
            f"I couldn't find order **{order_id}** "
            f"under **{account_name}**."
        )

    order = order_result["data"]

    if order["status"] != "BOOKED":

        return (
            f"Order **{order_id}** cannot be cancelled.\n\n"
            f"**Current status:** {order['status']}"
        )

    pending_action = {
        "action": "cancel_order",
        "account_id": account["account_id"],
        "account_name": account["account_name"],
        "order_id": order_id,
    }

    return (
        f"I found order **{order_id}** for "
        f"**{account['account_name']}**.\n\n"
        f"**Account ID:** {account['account_id']}\n"
        f"**Current status:** {order['status']}\n"
        f"**Pickup completed:** "
        f"{'Yes' if order.get('pickup_actual_at') else 'No'}\n\n"
        "Would you like me to proceed with cancelling "
        f"**{order_id}**?\n\n"
        "Please reply **Yes** or **No**."
    )


# ============================================================
# ASK AGENT
# ============================================================

def ask_agent(user_message):

    global pending_action

    user_message = user_message.strip()

    if not user_message:
        return "Please enter a message."

    # ========================================================
    # PENDING ACTION
    # ========================================================

    if pending_action:

        # Waiting for account for cancellation
        if (
            pending_action.get("action")
            == "awaiting_cancel_account"
        ):

            account_name = user_message

            account = resolve_account(
                account_name
            )

            if not account:

                return (
                    f"I couldn't find the account "
                    f"**{account_name}**."
                )

            order_id = pending_action["order_id"]

            order_result = lookup_order(
                order_id=order_id,
                account_id=account["account_id"]
            )

            if not order_result.get("found"):

                pending_action = None

                return (
                    f"I couldn't find order **{order_id}** "
                    f"under **{account_name}**."
                )

            order = order_result["data"]

            if order["status"] != "BOOKED":

                pending_action = None

                return (
                    f"Order **{order_id}** cannot be cancelled.\n\n"
                    f"**Current status:** {order['status']}"
                )

            pending_action = {
                "action": "cancel_order",
                "account_id": account["account_id"],
                "account_name": account["account_name"],
                "order_id": order_id,
            }

            return (
                f"I found order **{order_id}** for "
                f"**{account['account_name']}**.\n\n"
                f"**Account ID:** {account['account_id']}\n"
                f"**Current status:** {order['status']}\n\n"
                f"Would you like me to cancel **{order_id}**?\n\n"
                "Please reply **Yes** or **No**."
            )

        result = handle_pending_action(
            user_message
        )

        if result:
            return result

    # ========================================================
    # SECURITY-FIRST ESCALATION
    # ========================================================

    escalation_result = handle_escalation_request(
        user_message
    )

    if escalation_result:
        return escalation_result

    # ========================================================
    # CANCELLATION
    # ========================================================

    cancellation_result = handle_cancellation_request(
        user_message
    )

    if cancellation_result:
        return cancellation_result

    # ========================================================
    # NORMAL GROQ AGENT
    # ========================================================

    messages = [
        {
            "role": "system",
            "content": SYSTEM_INSTRUCTION
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    while True:

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )

        message = response.choices[0].message

        if not message.tool_calls:

            return message.content

        messages.append(message)

        for tool_call in message.tool_calls:

            function_name = tool_call.function.name

            arguments = json.loads(
                tool_call.function.arguments
            )

            # =================================================
            # SECURITY ENFORCEMENT FOR LOOKUP TICKET
            # =================================================

            if function_name == "lookup_ticket":

                ticket_id = arguments["ticket_id"]
                account_id = arguments.get("account_id")

                tool_result = secure_ticket_lookup(
                    ticket_id=ticket_id,
                    requested_account_id=account_id
                )

            else:

                tool_result = execute_tool(
                    function_name,
                    arguments
                )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(
                        tool_result,
                        default=str
                    )
                }
            )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PARCELPILOT AI SUPPORT AGENT - GROQ")
    print("=" * 60)
    print(
        "Type 'exit' or 'quit' to end the conversation."
    )

    while True:

        question = input("\nUser: ").strip()

        if question.lower() in {
            "exit",
            "quit"
        }:

            print("\n👋 Goodbye!")
            break

        if not question:
            continue

        try:

            answer = ask_agent(question)

            print(
                f"\n🤖 Agent:\n{answer}"
            )

        except Exception as error:

            print(
                f"\n❌ Error: {error}"
            )