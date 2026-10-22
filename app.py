import threading
from datetime import datetime
from zoneinfo import ZoneInfo

import requests
import streamlit as st
from openai import OpenAI

# 1. Page Configuration (Looks sharp on a big projector screen)
st.set_page_config(page_title="IDA Presentation Chatbot", page_icon="🤖", layout="centered")

st.title("🤖 IDA Presentation Q&A Bot")
st.caption("Ask me anything about today's presentation topic! Powered by OpenAI Responses API.")

# 2. Sidebar Configuration for Credentials
st.sidebar.header("⚙️ Configuration")

try:
    default_key = st.secrets.get("OPENAI_API_KEY", "")
except Exception:
    default_key = ""

api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=default_key)

if not api_key:
    st.info("Please add your OpenAI API Key in the sidebar to begin.", icon="🔑")
    st.stop()

# Google Sheet logging (optional): URL of the Apps Script web app in google_apps_script/Code.gs
try:
    sheet_webhook_url = st.secrets.get("GOOGLE_SHEET_WEBHOOK_URL", "")
except Exception:
    sheet_webhook_url = ""

def log_to_google_sheet(question, answer):
    """Append Timestamp | User_Question | AI_Answer to the Google Sheet without blocking the chat."""
    if not sheet_webhook_url:
        return
    payload = {
        "timestamp": datetime.now(ZoneInfo("Asia/Singapore")).strftime("%Y-%m-%d %H:%M:%S"),
        "question": question,
        "answer": answer,
    }

    def send():
        try:
            requests.post(sheet_webhook_url, json=payload, timeout=15)
        except Exception as e:
            print(f"Google Sheet logging failed: {e}")

    threading.Thread(target=send, daemon=True).start()

# Initialize the OpenAI Client
client = OpenAI(api_key=api_key)

# 3. Persistent Conversation Management (Stores chat state across queries)
if "messages" not in st.session_state:
    st.session_state.messages = []

if "conversation_id" not in st.session_state:
    conversation = client.conversations.create()
    st.session_state.conversation_id = conversation.id

# Define your Subject Matter Expert rules directly in code
SYSTEM_INSTRUCTIONS = """
You are an expert Subject Matter Expert chatbot for the IDA presentation. 
Answer user questions accurately. Keep your answers brief and limited to a maximum of 3 sentences 
so they are easy to read on mobile phones and presentation screens. 
If you don't know the answer based on the knowledge base, politely state that you do not know.
"""

# 4. Display Chat History
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# 5. Handle Live Interaction
if user_query := st.chat_input("Ask a question about the presentation..."):
    # Display user question instantly
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user"):
        st.markdown(user_query)

    # 6. Call the modern Responses API
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            response = client.responses.create(
                model="gpt-5",  
                instructions=SYSTEM_INSTRUCTIONS,
                conversation=st.session_state.conversation_id,
                input=[{"role": "user", "content": user_query}],
                store=True,
                tools=[{
                    "type": "file_search",
                    "vector_store_ids": ["vs_6ad8ec212788819181221d747227c4a1"]
                }]
            )
            
            assistant_response = response.output_text
            response_placeholder.markdown(assistant_response)
            
            # Save to local session states for re-renders
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})

            # Capture the Q&A in the Google Sheet
            log_to_google_sheet(user_query, assistant_response)
            
        except Exception as e:
            response_placeholder.markdown(f"⚠️ API Error: {str(e)}")
