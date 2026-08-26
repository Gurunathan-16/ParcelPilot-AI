# 📦 ParcelPilot AI Support Agent

An AI-powered customer support agent for ParcelPilot, a B2B logistics platform.

The system helps support teams answer questions about **customer accounts, orders, support tickets, cancellation policies, customer-specific agreements, service credits, and escalations**.

The main design goal is **reliable tool-based decision making instead of allowing the LLM to invent operational data**.

---

## 🚀 Key Features

* Natural-language customer support
* Customer account lookup
* Order lookup and status verification
* Support ticket lookup
* Policy and SOP document search
* Customer-specific agreement retrieval
* Customer agreement vs. general policy reasoning
* Order cancellation workflow
* Explicit confirmation before state-changing actions
* Ticket escalation workflow
* Account and ticket ownership validation
* Groq LLM tool calling
* FastAPI backend
* Streamlit chat interface
* CLI interface for local testing
* Structured operational data handling
* Document-based policy retrieval

---

# 🏗️ Solution Architecture

```text
                         ┌─────────────────────┐
                         │        User         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │    Streamlit UI     │
                         └──────────┬──────────┘
                                    │
                                    ▼
                         ┌─────────────────────┐
                         │     FastAPI API     │
                         │       /chat         │
                         └──────────┬──────────┘
                                    │
                                    ▼
                     ┌────────────────────────────┐
                     │     ParcelPilot Agent      │
                     │                            │
                     │       Groq LLM             │
                     │     Tool Calling            │
                     └─────────────┬──────────────┘
                                   │
               ┌───────────────────┼───────────────────┐
               │                   │                   │
               ▼                   ▼                   ▼
       ┌──────────────┐    ┌──────────────┐    ┌──────────────┐
       │    Account   │    │    Orders    │    │   Tickets    │
       │    Lookup    │    │    Lookup    │    │    Lookup    │
       └──────────────┘    └──────────────┘    └──────────────┘
                                   │
                                   ▼
                         ┌─────────────────────┐
                         │  Document Search    │
                         └──────────┬──────────┘
                                    │
                         ┌──────────┴──────────┐
                         ▼                     ▼
                 Customer Agreements        SOPs
```

The assessment explicitly requires document retrieval, structured-data lookup, state-changing actions, multi-step requests, and confirmation before state changes.

---

# 🧠 Agent Design

The agent uses **Groq's LLM tool-calling capability**.

The LLM does not directly access the application's business data. Instead, it selects appropriate tools.

### Available tools

| Tool                | Purpose                                             |
| ------------------- | --------------------------------------------------- |
| `lookup_account`    | Retrieve customer account information               |
| `lookup_order`      | Retrieve order information                          |
| `lookup_ticket`     | Retrieve support ticket information                 |
| `search_documents`  | Search policies, SOPs, agreements and documentation |
| `cancel_order`      | Cancel an eligible order                            |
| `create_escalation` | Create a support escalation                         |

This follows the assessment requirement that the agent have distinct document-search, structured-data, and state-changing capabilities.

---

# 🔐 Reliability and Trust

ParcelPilot's source data is intentionally imperfect. Policies can become outdated, customer agreements can override general policies, and historical ticket information may contain incorrect guidance.

The agent therefore follows these principles:

1. **Never invent operational data.**
2. Use account lookup for account information.
3. Use order lookup for order information.
4. Use ticket lookup for ticket information.
5. Use document search for policies, SOPs and agreements.
6. Customer-specific agreements override general policies when they explicitly provide different terms.
7. Current policies take precedence over deprecated policies.
8. Verify ticket ownership before exposing ticket information.
9. Never execute state-changing operations without confirmation.
10. When information is unavailable or conflicting, avoid making unsupported claims.

---

# 📄 Document and Policy Handling

The document collection includes:

* Current support policy
* Deprecated support policy
* Cancellation & Service Credit SOP
* Product operations documentation
* Northstar Logistics Enterprise Agreement
* LumenWorks Service Agreement

The supplied assessment data also contains structured account, order and ticket information.

### Policy precedence

The agent follows this general hierarchy:

```text
Customer-specific agreement
            │
            ▼
Current ParcelPilot policy / SOP
            │
            ▼
Historical / deprecated information
```

If a customer agreement explicitly changes a rule, that agreement is applied.

For example:

### Northstar Logistics

Northstar has a customer-specific cancellation rule allowing BOOKED shipments to be cancelled before pickup without a cancellation fee.

### LumenWorks

LumenWorks does not have a special cancellation-fee waiver, so the current ParcelPilot cancellation SOP applies.

---

# 🛡️ Safe State-Changing Actions

Actions that modify system state require explicit confirmation.

For example:

```text
User:
Cancel ORD-1001
```

The agent first verifies:

```text
Account
   ↓
Order
   ↓
Order status
   ↓
Eligibility
```

It then asks:

```text
Would you like me to cancel ORD-1001?

Please reply Yes or No.
```

Only after an explicit confirmation does the cancellation action execute.

The same pattern is used for escalations.

This follows the assessment requirement that every state-changing action require explicit user confirmation.

---

# 🔄 Multi-Step Reasoning

The system supports requests requiring multiple sources.

Example:

```text
Can Northstar Logistics cancel ORD-1001 without a cancellation fee?
```

The agent can perform:

```text
1. Identify Northstar Logistics
        ↓
2. Lookup account
        ↓
3. Lookup ORD-1001
        ↓
4. Retrieve Northstar agreement
        ↓
5. Retrieve current cancellation SOP
        ↓
6. Compare applicable rules
        ↓
7. Produce the answer
```

This type of multi-source workflow is specifically required by the assessment.

---

# 🖥️ Application Interfaces

## Streamlit

The Streamlit application provides the customer-support chat interface.

```text
Streamlit
    ↓
POST /chat
    ↓
FastAPI
    ↓
ParcelPilot Agent
```

For the deployed application, the Streamlit frontend can communicate with the hosted FastAPI backend.

For local development:

```text
Streamlit
    ↓
http://127.0.0.1:8000/chat
    ↓
Local FastAPI
```

---

# ⚙️ Technology Stack

| Technology               | Purpose                    |
| ------------------------ | -------------------------- |
| Python                   | Core application           |
| Groq                     | LLM and tool calling       |
| GPT-OSS-20B              | Agent model                |
| FastAPI                  | Backend API                |
| Streamlit                | User interface             |
| SQLite / structured data | Operational records        |
| Document retrieval       | Policies and agreements    |
| Pydantic                 | API/data validation        |
| python-dotenv            | Environment configuration  |
| Requests                 | Frontend API communication |

---

# 📁 Project Structure

```text
parcelpilot-ai/
│
├── app/
│   ├── agent/
│   │   ├── groq_agent.py
│   │   ├── tools.py
│   │   ├── actions.py
│   │   └── confirmation.py
│   │
│   ├── api/
│   │   └── session_manager.py
│   │
│   ├── main.py
│   └── ui.py
│
├── data/
│   ├── accounts/
│   ├── orders/
│   ├── tickets/
│   └── documents/
│
├── requirements.txt
├── .env
├── .gitignore
└── README.md
```

---

# 🔧 Installation

Clone the repository:

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd parcelpilot-ai
```

Create a virtual environment:

### Windows

```bash
python -m venv venv
venv\Scripts\activate
```

### macOS / Linux

```bash
python3 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key
```

Do not commit `.env` or API keys to GitHub.

---

# ▶️ Run the Backend

Start FastAPI:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

---

# ▶️ Run the Streamlit Frontend

Open another terminal:

```bash
streamlit run app/ui.py
```

The Streamlit application will open in the browser.

For local development, configure:

```python
API_URL = "http://127.0.0.1:8000/chat"
```

For a deployed frontend communicating with the hosted backend, configure the deployed API URL instead.

---

# 🧪 CLI Testing

The agent can also be tested directly:

```bash
python -m app.agent.groq_agent
```

Example:

```text
User: What is the account ID for Northstar Logistics?

Agent:
The account ID for Northstar Logistics is:

ACCT-001
```

Another example:

```text
User: What is the account ID for LumenWorks?

Agent:
The account ID for LumenWorks is:

ACCT-002
```

---

# 💬 Example Queries

### Account

```text
What is the account ID for Northstar Logistics?
```

```text
What is the account ID for LumenWorks?
```

### Orders

```text
What is the status of ORD-1001?
```

```text
Show me the details for ORD-1001.
```

### Cancellation

```text
Can Northstar Logistics cancel ORD-1001 without a cancellation fee?
```

```text
Does LumenWorks have special cancellation terms?
```

```text
Cancel ORD-1001.
```

### Tickets

```text
What is the status of TKT-1001?
```

```text
Escalate TKT-1001.
```

### Policies

```text
What is the current cancellation policy?
```

```text
What service credit applies to a failed pickup?
```

---

# 🎯 Important Product Decisions

## 1. Tool Calling Instead of LLM-Only Answers

Business information such as account IDs, order status and ticket data comes from application tools.

This reduces hallucination and keeps operational information tied to the underlying data.

---

## 2. Customer Agreements Override General Policies

A generic policy cannot always answer a customer-specific question.

Therefore, the agent checks for an applicable customer agreement before applying the general SOP.

---

## 3. Confirmation Before State Changes

Cancellation and escalation can modify system state.

The agent therefore separates:

```text
Intent
  ↓
Validation
  ↓
Confirmation
  ↓
Action
```

This prevents accidental state changes.

---

## 4. Account/Ticket Validation

Before working with an order or ticket, the system validates the associated account.

This helps prevent accidental access to information belonging to another customer.

---

# 🧩 Assessment Requirements Covered

| Requirement                  | Implementation |
| ---------------------------- | -------------- |
| Natural-language chatbot     | ✅              |
| Document retrieval           | ✅              |
| Structured-data lookup       | ✅              |
| State-changing action        | ✅              |
| Explicit confirmation        | ✅              |
| Multi-step requests          | ✅              |
| Account validation           | ✅              |
| Ticket validation            | ✅              |
| Customer-specific agreements | ✅              |
| Current policy handling      | ✅              |
| Simple chat interface        | ✅              |
| Hosted backend               | ✅              |

The assessment requires the chatbot to use the supplied data, support multiple tools/sources, handle state-changing actions safely, and provide a simple interface.

---

# 🎥 Demo Video

The project includes a roughly 5-minute technical/product demonstration covering:

### 1. Solution Architecture

* Streamlit frontend
* FastAPI backend
* Groq agent
* Tool-calling layer
* Structured data
* Document retrieval

### 2. Working Application

Demonstration scenarios:

```text
Account lookup
        ↓
Policy lookup
        ↓
Customer agreement reasoning
        ↓
Order lookup
        ↓
Cancellation confirmation
        ↓
State-changing action
```

### 3. Technical Decisions

The video explains:

* Why tool calling is used
* Why customer agreements are separated from general SOPs
* Why confirmation is required before actions
* How account and ticket validation improves reliability

The assessment specifically requests a roughly five-minute video covering architecture, a working application demonstration, and important product/technical decisions.

---

# 📌 Hosted Application

Backend:

```text
https://parcelpilot-ai-nraw.onrender.com
```

FastAPI endpoint:

```text
POST /chat
```

Swagger:

```text
/docs
```

> Replace these deployment details with the final production URLs if the hosting configuration changes.

---

# 🔒 Security

The following should never be committed to the repository:

```text
.env
API keys
credentials
private production data
```

Use environment variables for secrets.

Example `.gitignore`:

```gitignore
.env
venv/
__pycache__/
*.pyc
.streamlit/secrets.toml
```

---

# 🚧 Current Limitations

* The current agent is primarily focused on customer support workflows.
* State-changing operations use application-level confirmation.
* Document retrieval quality depends on the supplied source documents.
* The current UI is intentionally simple for the assessment.
* Session state should be persisted in a shared store before scaling the application horizontally.
* Advanced proactive issue detection is not part of the current core implementation.

---

# 🔮 Future Improvements

If development continued, the next priorities would be:

### 1. Proactive Issue Detection

Build an internal operations dashboard that identifies:

* Recurring customer complaints
* Multiple tickets related to the same issue
* SLA breaches
* Unusual order patterns
* Issues affecting multiple customers

This directly addresses one of ParcelPilot's broader client problems.

### 2. Better Observability

Add:

* Tool-call logging
* Latency tracking
* Token/cost monitoring
* Error monitoring
* Agent evaluation metrics

### 3. Evaluation Framework

Create automated tests for:

* Correct tool selection
* Policy precedence
* Account isolation
* Cancellation safety
* Hallucination resistance
* Conflicting document handling

### 4. Production-Grade State Management

Move pending actions from process memory to a persistent/shared store so the application can safely run across multiple backend instances.

---

# 📊 Success Metric

A useful primary metric for the product would be:

> **Percentage of support requests resolved correctly without human intervention.**

This combines answer quality and operational usefulness rather than measuring chatbot activity alone.

---

# 🤖 AI Tool Usage

AI coding assistance was used during development for:

* Debugging Python errors
* Refactoring the agent architecture
* Designing tool-calling workflows
* Improving prompts
* Building API/UI integration
* Reviewing edge cases
* Preparing documentation

All application behavior was validated against the supplied ParcelPilot data and workflows.

---

# 👨‍💻 Author

**Gurunathan R**

M.Sc. Computer Science

Focus:

* AI Engineering
* Generative AI
* LLM Applications
* AI Agents
* RAG
* Python Backend Development

---

## ⭐ Project Goal

ParcelPilot AI Support Agent is designed around one principle:

> **Use the LLM for reasoning, but use reliable tools and source data for facts and actions.**

This separation makes the system more reliable, safer for business workflows, and easier to extend into a production customer-support platform.