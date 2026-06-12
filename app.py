import streamlit as st
import time
from google import genai
from google.genai import types

# 1. Page Configuration & UI Theme Styling
st.set_page_config(page_title="FinGuard Dashboard", page_icon="🛡️", layout="wide")

# Custom CSS for a beautiful Enterprise Fintech look
st.markdown("""
    <style>
    /* Main Background & Fonts */
    .stApp {
        background-color: #0d1117;
        color: #c9d1d9;
    }
    
    /* Custom Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid #30363d;
    }
    
    /* Metrics and Headers */
    .main-title {
        font-size: 2.5rem;
        font-weight: 800;
        background: linear-gradient(45deg, #1f6feb, #4ffbdf);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    
    .subtitle {
        color: #8b949e;
        font-size: 1rem;
        margin-bottom: 2rem;
    }
    
    /* Metric Card Styling */
    .metric-card {
        background-color: #21262d;
        border: 1px solid #30363d;
        border-radius: 10px;
        padding: 15px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    .metric-value {
        font-size: 1.8rem;
        font-weight: bold;
        color: #58a6ff;
    }
    
    /* Beautiful Chat Styling overrides */
    div[data-testid="stChatMessage"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 12px;
        padding: 15px;
        margin-bottom: 10px;
    }
    
    div[data-testid="stChatMessage"]:nth-child(even) {
        background-color: #21262d;
    }
    </style>
""", unsafe_allow_html=True)

# 2. Initialize Core State Data
if "client" not in st.session_state:
    st.session_state.client = genai.Client()

if "db" not in st.session_state:
    st.session_state.db = [
        {"transaction_id": "TXN001", "vendor": "CloudHosting Services", "amount": 12500, "status": "Settled"},
        {"transaction_id": "TXN002", "vendor": "SaaSFlow CRM", "amount": 4500, "status": "Settled"},
        {"transaction_id": "TXN003", "vendor": "Global Logistics Corp", "amount": 32000, "status": "Settled"},
    ]

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- EXPLICIT CAPABILITY TOOLS ---
def add_transaction(vendor: str, amount: int, status: str = "Pending") -> dict:
    new_id = f"TXN{len(st.session_state.db) + 1:03d}"
    new_record = {"transaction_id": new_id, "vendor": vendor, "amount": amount, "status": status}
    st.session_state.db.append(new_record)
    st.sidebar.success(f"💾 Ledger Updated: Added {new_id}")
    return {"success": True, "message": f"Successfully registered transaction {new_id}."}

def audit_transactions(min_amount: int = 0) -> dict:
    """
    Scans the entire corporate ledger database transactions to identify duplicate billing anomalies, 
    fraud risks, or double entries matching any specified minimum dollar amount thresholds.
    """
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


# 3. Sidebar UI (The Database Monitor)
st.sidebar.markdown("### 📊 Ledger Database Control")
st.sidebar.markdown("This sidebar tracks all live JSON transactional structures currently saved inside system memory.")
st.sidebar.dataframe(st.session_state.db, use_container_width=True)

# Calculate dynamic statistics for dashboard look
total_spend = sum(item['amount'] for item in st.session_state.db)
total_txns = len(st.session_state.db)

st.sidebar.markdown("---")
st.sidebar.markdown("### 📈 Live Analytics")
st.sidebar.markdown(f"**Total Tracked Volume:** ${total_spend:,}")
st.sidebar.markdown(f"**Ledger Row Count:** {total_txns}")


# 4. Layout Columns for Main Panel
st.markdown("<div class='main-title'>🛡️ FinGuard Risk Control Center</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Autonomous Financial Risk Assessment & Audit Environment</div>", unsafe_allow_html=True)

# Dynamic Metric Grid
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown("<div class='metric-card'>Ledger Integrity Status<br><div class='metric-value' style='color:#3fb950;'>SECURE</div></div>", unsafe_allow_html=True)
with col2:
    st.markdown(f"<div class='metric-card'>Total Monitored Outflow<br><div class='metric-value'>${total_spend:,}</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown(f"<div class='metric-card'>Connected Extensions<br><div class='metric-value' style='color:#a371f7;'>2 Active</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# 5. Core System Instructions Setup
system_instruction = """
You are FinGuard, an autonomous financial risk audit agent.
You possess two tools: 'add_transaction' and 'audit_transactions'.

CRITICAL HANDLING INSTRUCTIONS:
- If the user asks to look for duplicate billing anomalies, double counts, or fraud, you MUST run the 'audit_transactions' tool. If they don't give a threshold value, default to min_amount=0.
- When summarizing findings, structure your answers cleanly inside Markdown formatting tables.
"""


# Render Interactive Chat Log Window
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Chat Portal
if user_query := st.chat_input("Command FinGuard (e.g., 'Log transaction for Global Logistics' or 'Run duplicate audit')"):
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})

    # Agent Engine Reasoning Call
    with st.chat_message("assistant"):
        with st.spinner("FinGuard analyzing context and dispatching security tools..."):
            try:
                response = st.session_state.client.models.generate_content(
                    model='gemini-2.5-flash',
                    contents=user_query,
                    config=types.GenerateContentConfig(
                        system_instruction=system_instruction,
                        tools=[add_transaction, audit_transactions],
                        temperature=0.1,
                    )
                )
                st.markdown(response.text)
                st.session_state.messages.append({"role": "assistant", "content": response.text})
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"Gateway Intercept Rate Threshold hit: {e}. Please retry turn shortly.")