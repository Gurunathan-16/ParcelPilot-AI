import streamlit as st
import requests

st.set_page_config(
    page_title="ParcelPilot AI Support",
    page_icon="📦"
)

st.title("📦 ParcelPilot AI Support")
st.caption("AI-powered customer support agent")

API_URL = "http://127.0.0.1:8000/chat"

message = st.text_input(
    "Ask ParcelPilot",
    placeholder="What is the account ID for Northstar Logistics?"
)

if st.button("Send", type="primary"):

    if not message.strip():
        st.warning("Please enter a message.")
    else:
        try:
            response = requests.post(
                API_URL,
                json={"message": message},
                timeout=120
            )

            if response.status_code == 200:
                data = response.json()

                st.markdown("### 🤖 Agent")

                # Your FastAPI currently returns "message"
                st.markdown(data.get("message", "No response received."))

            else:
                st.error(
                    f"API Error {response.status_code}: "
                    f"{response.text}"
                )

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to FastAPI. "
                "Make sure Uvicorn is running on port 8000."
            )

        except Exception as e:
            st.error(f"Error: {e}")