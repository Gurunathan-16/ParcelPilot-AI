import streamlit as st
import requests

st.set_page_config(
    page_title="ParcelPilot AI Support",
    page_icon="📦"
)

st.title("📦 ParcelPilot AI Support")
st.caption("AI-powered customer support agent")

# Change this to your Render backend URL before deployment
API_URL = "https://parcelpilot-ai-nraw.onrender.com/chat"

message = st.text_input(
    "Ask ParcelPilot",
    placeholder="Ask about an account, order, ticket, cancellation, etc."
)

if st.button("Send", type="primary"):

    if not message.strip():
        st.warning("Please enter a message.")
    else:
        try:
            with st.spinner("Agent is thinking..."):

                response = requests.post(
                    API_URL,
                    json={"message": message},
                    timeout=120
                )

            if response.status_code == 200:

                data = response.json()

                st.markdown("### 🤖 Agent")

                st.markdown(
                    data.get(
                        "message",
                        "No response received."
                    )
                )

            else:
                st.error(
                    f"API Error {response.status_code}: "
                    f"{response.text}"
                )

        except requests.exceptions.Timeout:
            st.error("The agent took too long to respond.")

        except requests.exceptions.ConnectionError:
            st.error(
                "Cannot connect to the ParcelPilot API. "
                "Please check that the Render backend is running."
            )

        except Exception as e:
            st.error(f"Error: {e}")