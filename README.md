# ParcelPilot AI Support Agent

An AI-powered customer support agent that helps support teams retrieve account, ticket, and order information and perform authorized support actions using natural language.

## 🚀 Features

* 🤖 **AI-Powered Conversations** — Uses the Groq LLM API to understand customer support requests.
* 🔍 **Account Lookup** — Find customer accounts using account names or IDs.
* 🎫 **Ticket Management** — Retrieve support ticket details with account-level validation.
* 📦 **Order Lookup** — Check order status and details securely.
* ❌ **Order Cancellation** — Cancel eligible orders through a confirmation workflow.
* 🚨 **Ticket Escalation** — Escalate support tickets after user confirmation.
* 🔐 **Access Control** — Account-level authorization prevents cross-account access.
* 📄 **Document Search** — Retrieves relevant information from customer agreements and support policies.
* ⚡ **FastAPI Backend** — Provides REST API endpoints for the AI agent.
* 🖥️ **Streamlit UI** — Simple chat interface for interacting with the agent.
* 🗄️ **SQLite Database** — Stores account, order, and ticket data.

---

## 🏗️ Architecture

```text
User
 │
 ▼
Streamlit Chat UI
 │
 ▼
FastAPI Backend
 │
 ▼
ParcelPilot AI Agent
 │
 ├── Groq LLM
 │
 ├── Account & Order Tools
 │
 ├── Ticket Tools
 │
 ├── Access Control
 │
 └── SQLite Database
```

The LLM interprets the user's request and selects the appropriate tool. Sensitive actions such as order cancellation and ticket escalation require confirmation before execution.

---

## 🛠️ Technology Stack

| Technology | Purpose                   |
| ---------- | ------------------------- |
| Python     | Core programming language |
| Groq API   | LLM inference             |
| FastAPI    | Backend API               |
| Streamlit  | Web user interface        |
| SQLite     | Database                  |
| Pydantic   | Request validation        |

---

## 📂 Project Structure

```text
parcelpilot-ai/
│
├── app/
│   ├── agent/
│   │   ├── groq_agent.py       # AI agent and LLM integration
│   │   ├── tools.py            # Agent tools
│   │   └── actions.py          # Order and escalation actions
│   │
│   ├── api/
│   │   └── main.py             # FastAPI application
│   │
│   ├── auth/
│   │   └── user_context.py     # User context
│   │
│   ├── data/
│   │   └── database.py         # Database connection
│   │
│   ├── security/
│   │   └── access_control.py   # Authorization logic
│   │
│   └── tools/
│       └── data_lookup.py      # Database lookup functions
│
├── ui/
│   └── app.py                  # Streamlit interface
│
├── .env.example
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/Gurunathan-16/ParcelPilot-AI.git
cd ParcelPilot-AI
```

### 2. Create a virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Create a `.env` file in the project root:

```env
GROQ_API_KEY=your_groq_api_key_here
```

> ⚠️ Never commit your `.env` file or API keys to GitHub.

---

## ▶️ Running the Application

### Start the FastAPI backend

```bash
uvicorn app.api.main:app --reload
```

The API will run at:

`http://127.0.0.1:8000`

### Start the Streamlit UI

Open another terminal and run:

```bash
streamlit run ui/app.py
```

The application will open in your browser.

---

## 💬 Example Queries

Try asking the agent:

```text
What is the account ID for Northstar Logistics?
```

```text
What is ticket TKT-501 for Northstar Logistics?
```

```text
What is the status of ORD-1001 for ACCT-001?
```

```text
Cancel ORD-1001
```

```text
Escalate ticket TKT-501 for Northstar Logistics
```

---

## 🔐 Security and Authorization

ParcelPilot includes account-level access control to prevent unauthorized access to customer data.

* Internal support users can access authorized customer accounts.
* Customer users can only access their own account.
* Ticket and order lookups validate account ownership.
* Sensitive actions require explicit user confirmation.
* API keys are stored in environment variables and excluded from version control.

---

## 🔄 Example Agent Workflow

### Order Cancellation

```text
User: Cancel ORD-1001
        ↓
Agent requests account information
        ↓
Agent verifies account and order ownership
        ↓
Agent checks the order status
        ↓
Agent asks for confirmation
        ↓
User: Yes
        ↓
Order cancellation is executed
```

### Ticket Escalation

```text
User: Escalate ticket TKT-501
        ↓
Agent retrieves ticket details
        ↓
Agent validates the associated account
        ↓
Agent prepares escalation details
        ↓
Agent asks for confirmation
        ↓
User: Yes
        ↓
Escalation is created
```

---

## 🎯 Key Learnings

This project demonstrates practical implementation of:

* LLM-powered AI agents
* Function/tool calling
* Agent workflows and state management
* Human-in-the-loop confirmation
* API development with FastAPI
* Database integration with SQLite
* Role and account-based access control
* Building an end-to-end AI application

---

## 🔮 Future Improvements

* JWT authentication and multi-user support
* Conversation memory using Redis or a database
* Role-based permissions with production identity providers
* Docker containerization
* Automated tests and CI/CD
* Monitoring and logging
* Production deployment

---

## 👨‍💻 Author

**Gurunathan R**

AI/ML Engineer | Generative AI Enthusiast

---

⭐ If you found this project interesting, consider giving the repository a star!
