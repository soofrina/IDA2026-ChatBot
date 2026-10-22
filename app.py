import streamlit as st
from openai import OpenAI

# 1. Page Configuration (Looks sharp on a big projector screen)
st.set_page_config(page_title="IDA Presentation Chatbot", page_icon="💬", layout="centered")

# DAS (Dyslexia Association of Singapore) colour theme + dyslexia-friendly styling.
# Base colours live in .streamlit/config.toml; this CSS adds the finer polish:
# Lexend font, larger text, generous line/letter spacing and brand accents.
DAS_CRIMSON = "#C8151D"  # slightly deepened DAS red so white text passes WCAG AA
DAS_ORANGE = "#F69159"
DAS_BROWN = "#9A5E38"

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Lexend:wght@400;600;700&display=swap');

    .stApp, .stApp h1, .stApp h2, .stApp h3, .stApp label, .stApp input, .stApp textarea,
    [data-testid="stMarkdownContainer"], [data-testid="stMarkdownContainer"] * {{
        font-family: 'Lexend', 'Verdana', 'Arial', sans-serif !important;
    }}
    .stApp {{
        font-size: 1.1rem;
        line-height: 1.7;
        letter-spacing: 0.02em;
        word-spacing: 0.08em;
    }}
    .stMarkdown p, .stMarkdown li {{
        font-size: 1.1rem;
        line-height: 1.7;
        text-align: left;
    }}
    em, i {{ font-style: normal; font-weight: 600; }}

    /* Thin brand stripe across the very top of the page */
    header[data-testid="stHeader"] {{
        background: #FFF8F0;
        border-top: 6px solid;
        border-image: linear-gradient(90deg, {DAS_CRIMSON} 0%, {DAS_ORANGE} 60%, {DAS_BROWN} 100%) 1;
    }}

    /* Hero banner */
    .das-hero {{
        background: linear-gradient(135deg, {DAS_CRIMSON} 0%, #E0452E 55%, {DAS_ORANGE} 100%);
        color: #FFFFFF;
        padding: 1.6rem 1.8rem;
        border-radius: 18px;
        margin: 0.5rem 0 1.5rem 0;
        box-shadow: 0 6px 18px rgba(154, 94, 56, 0.25);
    }}
    .das-hero h1 {{
        color: #FFFFFF;
        font-size: 2.1rem;
        font-weight: 700;
        line-height: 1.25;
        margin: 0 0 0.4rem 0;
        padding: 0;
    }}
    .das-hero p {{
        color: #FFFFFF;
        font-size: 1.15rem;
        margin: 0;
        opacity: 0.95;
    }}

    @media (max-width: 640px) {{
        .das-hero {{ padding: 1.2rem 1.2rem; }}
        .das-hero h1 {{ font-size: 1.6rem; }}
        .das-hero p {{ font-size: 1.05rem; }}
    }}

    /* Chat bubbles */
    [data-testid="stChatMessage"] {{
        border-radius: 16px;
        padding: 1rem 1.2rem;
        margin-bottom: 0.9rem;
        border: 1px solid #F3D9C6;
        background: #FFFFFF;
        box-shadow: 0 2px 6px rgba(45, 42, 38, 0.06);
    }}
    [data-testid="stChatMessage"]:has([aria-label="Chat message from user"]) {{
        background: #FDEBDD;
        border-left: 6px solid {DAS_ORANGE};
    }}
    [data-testid="stChatMessage"]:has([aria-label="Chat message from assistant"]) {{
        border-left: 6px solid {DAS_CRIMSON};
    }}

    /* Chat input */
    [data-testid="stChatInput"] {{
        border: 2px solid {DAS_ORANGE};
        border-radius: 14px;
    }}
    [data-testid="stChatInput"]:focus-within {{
        border-color: {DAS_CRIMSON};
    }}
    [data-testid="stChatInput"] textarea {{ font-size: 1.1rem; }}

    /* Sidebar */
    [data-testid="stSidebar"] {{
        background: #FDEBDD;
        border-right: 4px solid {DAS_ORANGE};
    }}
    [data-testid="stSidebar"] h2 {{ color: #7A4A2B; }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="das-hero">
        <h1>IDA Presentation Q&amp;A</h1>
        <p>Ask me anything about today's presentation. I'll keep answers short and clear.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

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
AVATARS = {"user": "🙋", "assistant": "💡"}

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar=AVATARS[message["role"]]):
        st.markdown(message["content"])

# 5. Handle Live Interaction
if user_query := st.chat_input("Ask a question about the presentation..."):
    # Display user question instantly
    st.session_state.messages.append({"role": "user", "content": user_query})
    with st.chat_message("user", avatar=AVATARS["user"]):
        st.markdown(user_query)

    # 6. Call the modern Responses API
    with st.chat_message("assistant", avatar=AVATARS["assistant"]):
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
            
        except Exception as e:
            response_placeholder.markdown(f"⚠️ API Error: {str(e)}")
