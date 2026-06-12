import os
import time
from google import genai
from google.genai import types

# 1. In-memory Database Simulation
LIVE_TRANSACTIONS = [
    {"transaction_id": "TXN001", "vendor": "CloudHosting Services", "amount": 12500, "status": "Settled"},
    {"transaction_id": "TXN002", "vendor": "SaaSFlow CRM", "amount": 4500, "status": "Settled"},
    {"transaction_id": "TXN003", "vendor": "Global Logistics Corp", "amount": 32000, "status": "Settled"},
]

# --- TOOL 1: Save a new transaction ---
def add_transaction(vendor: str, amount: int, status: str = "Pending") -> dict:
    """
    Saves a new corporate transaction to the ledger database.
    Use this tool whenever a user explicitly provides transaction details to log or save.
    """
    new_id = f"TXN{len(LIVE_TRANSACTIONS) + 1:03d}"
    new_record = {
        "transaction_id": new_id,
        "vendor": vendor,
        "amount": amount,
        "status": status
    }
    LIVE_TRANSACTIONS.append(new_record)
    print(f"\n💾 [DATABASE WRITE SUCCESS]: Added {new_record}")
    return {"success": True, "message": f"Successfully registered transaction {new_id}."}


# --- TOOL 2: Audit for anomalies ---
def audit_transactions(min_amount: int = 0) -> dict:
    """Scans corporate database transactions to flag duplicate billing anomalies."""
    seen = {}
    duplicates = []
    for txn in LIVE_TRANSACTIONS:
        if txn["amount"] >= min_amount:
            key = (txn["vendor"], txn["amount"])
            if key in seen:
                if seen[key] not in duplicates:
                    duplicates.append(seen[key])
                duplicates.append(txn)
            else:
                seen[key] = txn
                
    return {"risk_level": "HIGH" if duplicates else "LOW", "flagged_records": duplicates}


# 2. System Architecture Setup
system_instruction = """
You are FinGuard, an autonomous financial risk audit agent. 
You can take actions using two different tools:
1. Use 'add_transaction' if the user provides information to submit, log, or record a transaction.
2. Use 'audit_transactions' if the user wants to scan for risks, check balances, or look for duplicates.

Always summarize the confirmation actions or audit findings clearly using Markdown tables.
If duplicate records are found during an audit, highlight why they pose an operational risk.
"""

# Initialize Client
client = genai.Client()

print("====================================================")
print("🚀 FinGuard Autonomous Chat Session Initialized... ")
print("👉 Type your command or type 'exit' to quit.")
print("====================================================\n")

# --- TRUE LIVE INTERACTIVE CHAT LOOP ---
while True:
    try:
        # 1. Grab dynamic input live from your keyboard in the terminal
        user_message = input("\n[You]: ")
        
        # Check if user wants to kill the script
        if user_message.strip().lower() == 'exit':
            print("👋 Exiting FinGuard Agent Session. Goodbye!")
            break
            
        if not user_message.strip():
            continue

        # 2. Forward your input directly to Gemini
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                tools=[add_transaction, audit_transactions],
                temperature=0.2,
            )
        )
        
        # 3. Print the Agent's reasoning out
        print(f"\n[FinGuard]: {response.text}")
        
        # 4. Enforce a small pause right after the turn to protect against free tier spam flags
        time.sleep(4)

    except Exception as e:
        print(f"\n⚠️ An unexpected gateway break occurred: {e}")
        print("Please wait a moment before trying your next turn...")
        time.sleep(5)