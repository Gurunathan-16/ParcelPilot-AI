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


# ============================================================
# CONFIG
# ============================================================

load_dotenv(override=True)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise RuntimeError("GROQ_API_KEY is not configured.")

client = Groq(api_key=GROQ_API_KEY)

MODEL_NAME = "openai/gpt-oss-20b"


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """
You are ParcelPilot AI Support Agent.

You answer questions about:

- customer accounts
- orders
- support tickets
- cancellation policies
- customer agreements
- SOPs
- service credits
- escalations

Rules:

1. Never invent information.
2. For account information, use lookup_account.
3. For order information, use lookup_order.
4. For ticket information, use lookup_ticket.
5. For policies, agreements and SOPs, use search_documents.
6. Customer-specific agreements override general policies when they explicitly
   provide different terms.
7. Current SOPs override historical SOPs.
8. Never expose another customer's private ticket information.
9. Never perform a state-changing action without explicit confirmation.
10. Cancellation requires Yes/No confirmation.
11. Escalation requires Yes/No confirmation.
12. If a tool returns an account, use the returned account_id exactly.
13. If the user asks for an account ID, answer directly from lookup_account.
14. Do not interpret the entire user question as an account name.
15. Keep answers concise and factual.
"""


# ============================================================
# GROQ TOOLS
# ============================================================

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "lookup_account",
            "description": "Find a ParcelPilot customer account by customer/account name.",
            "parameters": {
                "type": "object",
                "properties": {
                    "account_name": {
                        "type": "string",
                        "description": "Customer name only, such as 'Northstar Logistics' or 'LumenWorks'."
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
            "description": "Find a ParcelPilot order by order ID, optionally restricted to an account.",
            "parameters": {
                "type": "object",
                "properties": {
                    "order_id": {
                        "type": "string"
                    },
                    "account_id": {
                        "type": "string"
                    }
                },
                "required": ["order_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "lookup_ticket",
            "description": "Find a support ticket.",
            "parameters": {
                "type": "object",
                "properties": {
                    "ticket_id": {
                        "type": "string"
                    },
                    "account_id": {
                        "type": "string"
                    }
                },
                "required": ["ticket_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_documents",
            "description": "Search ParcelPilot policies, SOPs, customer agreements and documentation.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string"
                    }
                },
                "required": ["query"]
            }
        }
    },
]


# ============================================================
# STATE
# ============================================================

pending_action = None


# ============================================================
# KNOWN ACCOUNTS
# ============================================================

KNOWN_ACCOUNTS = {
    "northstar logistics": "Northstar Logistics",
    "northstar": "Northstar Logistics",
    "lumenworks": "LumenWorks",
}


# ============================================================
# BASIC HELPERS
# ============================================================

def normalize(text):
    if not text:
        return ""

    text = str(text).strip().lower()
    text = re.sub(r"\s+", " ", text)

    return text


def extract_account_name(message):
    """
    Extract ONLY the customer name.

    Never return the entire user question.
    """

    normalized = normalize(message)

    # Longest names first
    for key in sorted(KNOWN_ACCOUNTS, key=len, reverse=True):
        if key in normalized:
            return KNOWN_ACCOUNTS[key]

    return None


def extract_order_id(message):
    match = re.search(
        r"\bORD-\d+\b",
        message,
        re.IGNORECASE
    )

    return match.group(0).upper() if match else None


def extract_ticket_id(message):
    match = re.search(
        r"\bTKT-\d+\b",
        message,
        re.IGNORECASE
    )

    return match.group(0).upper() if match else None


def is_yes(message):
    return normalize(message) in {
        "yes",
        "y",
        "yeah",
        "yep",
        "confirm",
        "confirmed",
    }


def is_no(message):
    return normalize(message) in {
        "no",
        "n",
        "nope",
        "cancel",
        "don't",
        "do not",
    }


# ============================================================
# ACCOUNT LOOKUP
# ============================================================

def resolve_account(account_name):
    if not account_name:
        return None

    print("\n🔧 Tool selected: lookup_account")
    print({
        "account_name": account_name
    })

    result = lookup_account(
        account_name=account_name
    )

    print("Tool result:", result)

    if not isinstance(result, dict):
        return None

    if not result.get("found"):
        return None

    return result.get("data")


# ============================================================
# ACCOUNT INFORMATION QUESTIONS
# ============================================================

def is_account_id_question(message):
    text = normalize(message)

    return (
        ("account id" in text or "account number" in text)
        and "order" not in text
        and "ticket" not in text
    )


def handle_account_question(message):
    """
    Handles:

    What is the account ID for Northstar Logistics?
    What is the account ID for LumenWorks?
    Tell me Northstar Logistics account ID.
    """

    if not is_account_id_question(message):
        return None

    account_name = extract_account_name(message)

    print("DEBUG account question:")
    print("message =", message)
    print("account_name =", account_name)

    if not account_name:
        return (
            "I couldn't identify the customer account in your question. "
            "Please provide the customer name."
        )

    account = resolve_account(account_name)

    if not account:
        return (
            f"I couldn't find the account **{account_name}**."
        )

    return (
        f"**{account['account_name']}**\n\n"
        f"**Account ID:** `{account['account_id']}`"
    )


# ============================================================
# DOCUMENT SEARCH
# ============================================================

def search_documents(query):
    print("\n🔧 Tool selected: search_documents")
    print({
        "query": query
    })

    result = search_documents_tool(
        query=query
    )

    print("Tool result:", result)

    return result or []


# ============================================================
# POLICY QUESTION
# ============================================================

def is_policy_question(message):
    text = normalize(message)

    keywords = [
        "cancellation",
        "cancel",
        "fee",
        "policy",
        "agreement",
        "special terms",
        "special cancellation",
        "service credit",
        "credit",
        "sla",
        "support terms",
    ]

    return any(
        keyword in text
        for keyword in keywords
    )


# ============================================================
# FIND CUSTOMER AGREEMENT
# ============================================================

def find_customer_agreement(account_name, account_id):

    queries = [
        f"{account_name} {account_id} customer agreement cancellation terms",
        f"{account_name} cancellation agreement",
    ]

    for query in queries:

        documents = search_documents(query)

        for document in documents:

            content = document.get(
                "content",
                ""
            )

            normalized_content = normalize(content)

            if (
                normalize(account_name) in normalized_content
                and "agreement" in normalized_content
            ):
                return document

    return None


# ============================================================
# AGREEMENT QUESTION
# ============================================================

def handle_agreement_question(message):

    if not is_policy_question(message):
        return None

    account_name = extract_account_name(message)

    if not account_name:
        return None

    account = resolve_account(account_name)

    if not account:
        return (
            f"I couldn't find the account **{account_name}**."
        )

    account_id = account["account_id"]

    agreement = find_customer_agreement(
        account_name,
        account_id
    )

    if not agreement:

        return (
            f"I found **{account_name}** "
            f"(Account ID: `{account_id}`), but I couldn't "
            "find a customer-specific agreement covering "
            "this question."
        )

    agreement_text = agreement.get(
        "content",
        ""
    )

    policy_documents = search_documents(
        "ParcelPilot current Cancellation & Service Credit SOP "
        "BOOKED PICKED_UP cancellation fee"
    )

    # --------------------------------------------------------
    # Ask Groq to summarize the actual retrieved documents
    # --------------------------------------------------------

    prompt = f"""
Customer: {account_name}
Account ID: {account_id}

Customer agreement:
{agreement_text}

Current ParcelPilot policy:
{json.dumps(policy_documents, default=str)}

User question:
{message}

Answer the user using ONLY the information above.

Important:
- Customer agreement overrides the general policy only when it explicitly
  provides different cancellation terms.
- Do not invent terms.
- If the agreement says there is no special waiver, say so.
- Clearly state which policy applies.
"""

    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0
    )

    return response.choices[0].message.content


# ============================================================
# CANCELLATION REQUEST
# ============================================================

def handle_cancellation_request(message):

    global pending_action

    order_id = extract_order_id(message)

    if not order_id:
        return None

    if "cancel" not in normalize(message):
        return None

    account_name = extract_account_name(message)

    if not account_name:

        pending_action = {
            "action": "awaiting_cancel_account",
            "order_id": order_id
        }

        return (
            f"I can help with order **{order_id}**.\n\n"
            "Please provide the customer account name "
            "associated with this order."
        )

    account = resolve_account(account_name)

    if not account:

        return (
            f"I couldn't find the account **{account_name}**."
        )

    account_id = account["account_id"]

    print("\n🔧 Tool selected: lookup_order")

    order_result = lookup_order(
        order_id=order_id,
        account_id=account_id
    )

    print("Tool result:", order_result)

    if not order_result.get("found"):

        return (
            f"I couldn't find order **{order_id}** "
            f"under **{account_name}**."
        )

    order = order_result["data"]

    # Security check
    if order.get("account_id") != account_id:

        return (
            f"I can't access order **{order_id}** "
            f"for **{account_name}**."
        )

    status = order.get("status")

    if status != "BOOKED":

        return (
            f"Order **{order_id}** cannot be cancelled.\n\n"
            f"**Current status:** {status}"
        )

    pending_action = {
        "action": "cancel_order",
        "account_id": account_id,
        "account_name": account_name,
        "order_id": order_id,
    }

    return (
        f"I found order **{order_id}** for "
        f"**{account_name}**.\n\n"
        f"**Account ID:** `{account_id}`\n"
        f"**Current status:** {status}\n"
        f"**Picked up:** "
        f"{'Yes' if order.get('pickup_actual_at') else 'No'}\n\n"
        f"Would you like me to cancel **{order_id}**?\n\n"
        "Please reply **Yes** or **No**."
    )


# ============================================================
# PENDING ACTION
# ============================================================

def handle_pending_action(message):

    global pending_action

    if not pending_action:
        return None

    action = pending_action.get("action")

    # --------------------------------------------------------
    # Waiting for account
    # --------------------------------------------------------

    if action == "awaiting_cancel_account":

        account_name = extract_account_name(message)

        if not account_name:
            account_name = message.strip()

        account = resolve_account(account_name)

        if not account:

            return (
                f"I couldn't find the account **{account_name}**."
            )

        order_id = pending_action["order_id"]

        result = lookup_order(
            order_id=order_id,
            account_id=account["account_id"]
        )

        if not result.get("found"):

            pending_action = None

            return (
                f"I couldn't find order **{order_id}** "
                f"under **{account['account_name']}**."
            )

        order = result["data"]

        if order.get("status") != "BOOKED":

            pending_action = None

            return (
                f"Order **{order_id}** cannot be cancelled.\n\n"
                f"**Current status:** {order.get('status')}"
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
            f"**Account ID:** `{account['account_id']}`\n"
            f"**Current status:** {order['status']}\n\n"
            f"Would you like me to cancel **{order_id}**?\n\n"
            "Please reply **Yes** or **No**."
        )

    # --------------------------------------------------------
    # Cancellation confirmation
    # --------------------------------------------------------

    if action == "cancel_order":

        if is_yes(message):

            account_id = pending_action["account_id"]
            order_id = pending_action["order_id"]

            print("\n🔧 Tool selected: cancel_order")

            result = cancel_order(
                account_id=account_id,
                order_id=order_id
            )

            print("Tool result:", result)

            pending_action = None

            if result.get("success"):

                return (
                    f"✅ Order **{order_id}** has been "
                    "successfully cancelled.\n\n"
                    f"**Account:** `{account_id}`\n"
                    "**Status:** CANCELLED"
                )

            return (
                f"❌ I could not cancel order "
                f"**{order_id}**.\n\n"
                f"{result.get('message', 'Unknown error.')}"
            )

        if is_no(message):

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
# ESCALATION
# ============================================================

def handle_escalation_request(message):

    global pending_action

    text = normalize(message)

    if not any(
        word in text
        for word in [
            "escalate",
            "escalation",
            "human support"
        ]
    ):
        return None

    account_name = extract_account_name(message)

    ticket_id = extract_ticket_id(message)

    if not account_name:

        return (
            "I can help create an escalation, but I need "
            "the customer account name or ticket ID first."
        )

    account = resolve_account(account_name)

    if not account:

        return (
            f"I couldn't find the account **{account_name}**."
        )

    account_id = account["account_id"]

    if ticket_id:

        result = lookup_ticket(
            ticket_id=ticket_id,
            account_id=account_id
        )

        if not result.get("found"):

            return (
                f"I can't escalate ticket **{ticket_id}** "
                f"for **{account_name}** because it isn't "
                "associated with that account."
            )

        ticket = result["data"]

        reason = (
            f"{ticket.get('subject', '')}: "
            f"{ticket.get('description', '')}"
        )

    else:

        reason = message

    pending_action = {
        "action": "create_escalation",
        "account_id": account_id,
        "account_name": account_name,
        "reason": reason,
        "ticket_id": ticket_id,
    }

    return (
        f"I found **{account_name}**.\n\n"
        f"**Account ID:** `{account_id}`\n\n"
        f"**Reason:** {reason}\n\n"
        + (
            f"**Ticket:** {ticket_id}\n\n"
            if ticket_id
            else ""
        )
        + "Would you like me to create the escalation?\n\n"
        "Please reply **Yes** or **No**."
    )


# ============================================================
# GROQ TOOL EXECUTION
# ============================================================

def execute_tool(function_name, arguments):

    print("\n🔧 Tool selected:", function_name)
    print("Arguments:", arguments)

    if function_name == "lookup_account":

        return lookup_account(
            account_name=arguments["account_name"]
        )

    if function_name == "lookup_order":

        return lookup_order(
            order_id=arguments["order_id"],
            account_id=arguments.get("account_id")
        )

    if function_name == "lookup_ticket":

        return lookup_ticket(
            ticket_id=arguments["ticket_id"],
            account_id=arguments.get("account_id")
        )

    if function_name == "search_documents":

        return search_documents_tool(
            query=arguments["query"]
        )

    return {
        "error": f"Unknown tool: {function_name}"
    }


# ============================================================
# GROQ AGENT
# ============================================================

def run_groq_agent(user_message):

    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": user_message
        }
    ]

    for _ in range(5):

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0
        )

        assistant_message = response.choices[0].message

        if not assistant_message.tool_calls:
            return assistant_message.content or "I couldn't generate a response."

        messages.append(assistant_message)

        for tool_call in assistant_message.tool_calls:

            function_name = tool_call.function.name

            try:
                arguments = json.loads(
                    tool_call.function.arguments
                )
            except json.JSONDecodeError:

                arguments = {}

            result = execute_tool(
                function_name,
                arguments
            )

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": function_name,
                    "content": json.dumps(
                        result,
                        default=str
                    )
                }
            )

    return "I couldn't complete the request after several tool calls."


# ============================================================
# MAIN ASK FUNCTION
# ============================================================

def ask_agent(user_message):

    global pending_action

    if not user_message:
        return "Please enter a message."

    user_message = user_message.strip()

    # ========================================================
    # 1. PENDING STATE
    # ========================================================

    if pending_action:

        result = handle_pending_action(
            user_message
        )

        if result:
            return result

    # ========================================================
    # 2. SIMPLE ACCOUNT QUESTIONS
    # IMPORTANT: MUST COME BEFORE POLICY/CANCELLATION
    # ========================================================

    result = handle_account_question(
        user_message
    )

    if result:
        return result

    # ========================================================
    # 3. ESCALATION
    # ========================================================

    result = handle_escalation_request(
        user_message
    )

    if result:
        return result

    # ========================================================
    # 4. ORDER CANCELLATION
    # ========================================================

    result = handle_cancellation_request(
        user_message
    )

    if result:
        return result

    # ========================================================
    # 5. CUSTOMER AGREEMENT / POLICY
    # ========================================================

    result = handle_agreement_question(
        user_message
    )

    if result:
        return result

    # ========================================================
    # 6. NORMAL GROQ AGENT
    # ========================================================

    return run_groq_agent(
        user_message
    )


# ============================================================
# CLI
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("PARCELPILOT AI SUPPORT AGENT")
    print("=" * 60)

    while True:

        question = input("\nUser: ").strip()

        if question.lower() in {
            "exit",
            "quit"
        }:
            print("Goodbye!")
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