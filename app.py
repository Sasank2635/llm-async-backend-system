import streamlit as st
import requests
import time

API_URL = "http://localhost:8252"

st.title("🧠 LLM Chat (Async + Queue)")
st.caption("Async LLM system with queue, retries, and priority scheduling")

# Input
user_id = st.text_input("User ID", "1")
message = st.text_area("Enter your message")

priority = st.selectbox("Priority", ["high", "medium", "low"])

if st.button("Send"):
    if message:
        # Step 1: Send async request
        response = requests.post(
            f"{API_URL}/chat_async",
            params={
                "user_id": user_id,
                "message": message,
                "priority": priority
            }
        )

        task_id = response.json()["task_id"]
        st.write(f"🆔 Task ID: {task_id}")

        # Step 2: Poll result
        result_placeholder = st.empty()

        while True:
            res = requests.get(f"{API_URL}/result/{task_id}")
            data = res.json()

            if data["status"] == "completed":
                result_placeholder.success(data["result"])
                break

            elif data["status"] == "failed":
                result_placeholder.error(data["error"])
                break

            else:
                result_placeholder.info(f"Status: {data['status']}")
                time.sleep(1)