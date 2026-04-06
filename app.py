import streamlit as st
from google import genai

# 🔐 Gemini client (uses Streamlit secrets)
client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])

st.title("🧠 LLM Chat (Async + Queue)")
st.caption("Async LLM system with queue, retries, and priority scheduling")

# Input
user_id = st.text_input("User ID", "1")
message = st.text_area("Enter your message")

priority = st.selectbox("Priority", ["high", "medium", "low"])

if st.button("Send"):
    if message:
        status_placeholder = st.empty()
        status_placeholder.info("Status: processing...")

        try:
            with st.spinner("Thinking..."):
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=message
                )

            status_placeholder.success("Status: completed ✅")
            st.success(response.text)

        except Exception as e:
            status_placeholder.error("Status: failed ❌")
            st.error(str(e))