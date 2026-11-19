import streamlit as st
import requests


# ============================================================
# PAGE
# ============================================================

st.set_page_config(
    page_title="ParcelPilot AI Support",
    page_icon="📦",
    layout="centered",
)

st.title("📦 ParcelPilot AI Support")
st.caption("AI-powered customer support agent")


# ============================================================
# API
# ============================================================

API_URL = "http://127.0.0.1:8000/chat"
#API_URL = "https://parcelpilot-ai-nraw.onrender.com/chat"

# ============================================================
# CHAT HISTORY
# ============================================================

if "messages" not in st.session_state:
    st.session_state.messages = []


for message in st.session_state.messages:

    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# ============================================================
# INPUT
# ============================================================

message = st.chat_input(
    "Ask about an account, order, ticket, policy, etc."
)


# ============================================================
# SEND
# ============================================================

if message:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    with st.chat_message("user"):
        st.markdown(message)

    try:

        with st.chat_message("assistant"):

            with st.spinner("Agent is thinking..."):

                response = requests.post(
                    API_URL,
                    json={
                        "message": message,
                    },
                    timeout=120,
                )

            if response.status_code == 200:

                data = response.json()

                answer = data.get(
                    "message",
                    "No response received.",
                )

                st.markdown(answer)

                st.session_state.messages.append(
                    {
                        "role": "assistant",
                        "content": answer,
                    }
                )

            else:

                error_message = (
                    f"API Error {response.status_code}: "
                    f"{response.text}"
                )

                st.error(error_message)

    except requests.exceptions.Timeout:

        st.error(
            "The agent took too long to respond."
        )

    except requests.exceptions.ConnectionError:

        st.error(
            "Cannot connect to the ParcelPilot API. "
            "Please check that the Render backend is running."
        )

    except Exception as error:

        st.error(
            f"Error: {error}"
        )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("ParcelPilot")

    st.write(
        "Ask questions about:"
    )

    st.write(
        """
        - Customer accounts
        - Orders
        - Support tickets
        - Cancellation policies
        - Customer agreements
        - Service credits
        - Escalations
        """
    )

    if st.button("Clear Chat"):

        st.session_state.messages = []

        st.rerun()