import asyncio
import os
import streamlit as st
from dotenv import load_dotenv
from agents import Agent, Runner, function_tool, set_default_openai_client
from openai import AsyncOpenAI

# 1. Page Configuration
st.set_page_config(page_title="AI Receptionist Demo", page_icon="🤖")

# 2. Authentication Logic
if "CLIENT_PASSWORD" in st.secrets:
    CORRECT_PASSWORD = st.secrets["CLIENT_PASSWORD"]
else:
    CORRECT_PASSWORD = "client123"

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

st.sidebar.title("🔒 Client Authentication")
input_pass = st.sidebar.text_input("Enter Access Key:", type="password")

if st.sidebar.button("Login"):
    if input_pass.strip() == CORRECT_PASSWORD:
        st.session_state.authenticated = True
        st.sidebar.success("Access Granted!")
        st.rerun()
    else:
        st.sidebar.error("Incorrect Password!")

if not st.session_state.authenticated:
    st.title("🤖 Business Receptionist AI Agent")
    st.info("👈 Please enter your authorized Access Key in the sidebar to unlock the chat.")
    st.stop()

# 3. OpenRouter / LLM Client Setup
load_dotenv()
openrouter_key = st.secrets.get("OPENROUTER_API_KEY") or os.getenv("OPENROUTER_API_KEY")

custom_client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=openrouter_key,
)
set_default_openai_client(custom_client)

# 4. Agent Function Tool (Local Session Logging)
@function_tool
async def save_business_lead(name: str, phone: str, service_required: str) -> str:
    """Saves client lead details."""
    print(f"\n[LEAD CAPTURED]: {name} | {phone} | {service_required}\n")
    return f"Lead saved successfully for {name}."

lead_agent = Agent(
    name="Business Lead Automation Agent",
    instructions="""
    Aapka naam 'Business_lead_agent' hai. Aap ek professional Business Receptionist AI Agent hain.
    Customer se politely unka Name, Phone Number, aur Service Requirement collect karein.
    Teeno details milne par 'save_business_lead' tool call karein.
    """,
    tools=[save_business_lead],
    model="openai/gpt-4o-mini"
)

# 5. Streamlit Chat Interface
st.title("🤖 Business Receptionist AI Agent")
st.caption("24/7 Intelligent Customer Lead Capture System")

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

for msg in st.session_state.chat_history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if user_input := st.chat_input("Type your message..."):
    st.session_state.chat_history.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    full_prompt = ""
    for msg in st.session_state.chat_history:
        role_label = "User" if msg["role"] == "user" else "Assistant"
        full_prompt += f"{role_label}: {msg['content']}\n"

    async def get_response():
        result = await Runner.run(lead_agent, input=full_prompt)
        return result.final_output

    response = asyncio.run(get_response())

    st.session_state.chat_history.append({"role": "assistant", "content": response})
    with st.chat_message("assistant"):
        st.markdown(response)
