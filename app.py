import streamlit as st
import time
from google import genai
from google.genai import types

# Set up page config
st.set_page_config(page_title="FinGuard Agent", page_icon="🚀", layout="centered")
st.title("🚀 FinGuard Autonomous Audit Agent")
st.caption("Autonomous financial risk assessment powered by Gemini 2.5 Flash")

# Initialize Client
if "client" not in st.session_state:
    st.session_state.client = genai.Client()

# Initialize In-Memory Database
if "db" not in st.session_state:
    st.session_state.db = [
        {"transaction_id": "TXN001", "vendor": "CloudHosting Services", "amount": 12500, "status": "Settled"},
        {"transaction_id": "TXN002", "vendor": "SaaSFlow CRM", "amount": 4500, "status": "Settled"},
        {"transaction_id": "TXN003", "vendor": "Global Logistics Corp", "amount": 32000, "status": "Settled"},
    ]

# Initialize Chat History
if "messages" not in st.session_state:
    st.session_state.messages = []

# --- TOOLS ---
def add_transaction(vendor: str, amount: int, status: str = "Pending") -> dict:
    new_id = f"TXN{len(st.session_state.db) + 1:03d}"
    new_record = {"transaction_id": new_id, "vendor": vendor, "amount": amount, "status": status}
    st.session_state.db.append(new_record)
    st.sidebar.success(f"💾 DB Write: Added {new_id}")
    return {"success": True, "message": f"Successfully registered transaction {new_id}."}

def audit_transactions(min_amount: int = 0) -> dict:
    seen = {}
    duplicates = []
    for txn in st.session_state.db:
        if txn["amount"] >= min_amount:
            key = (txn["vendor"], txn["amount"])
            if key in seen:
                if seen[key] not in duplicates: duplicates.append(seen[key])
                duplicates.append(txn)
            else:
                seen[key] = txn
    return {"risk_level": "HIGH" if duplicates else "LOW", "flagged_records": duplicates}

# Sidebar Database Viewer
st.sidebar.header("📦 Live Ledger Database")
st.sidebar.dataframe(st.session_state.db, use_container_width=True)

# System Instructions
system_instruction = """
You are FinGuard, an autonomous financial risk audit agent. 
You can take actions using two tools: 'add_transaction' and 'audit_transactions'.
Always summarize confirmation details or audit findings in clear Markdown tables.
"""

# Render past chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Input
if user_query := st.chat_input("Ask FinGuard to log a transaction or run an audit..."):
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Call Gemini Agent
    with st.chat_message("assistant"):
        with st.spinner("FinGuard is analyzing and executing tools..."):
            try:
                response = st.session_state.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_query,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        tools=[add_transaction, audit_transactions],
                        temperature=0.2,
                    )
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                time.sleep(2) # Protect Free Tier limits
                st.rerun()
            except Exception as e:
                st.error(f"Rate limit or API glitch: {e}. Try again in a few seconds.")