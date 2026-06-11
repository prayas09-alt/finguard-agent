import os
from flask import Flask, jsonify, request

app = Flask(__name__)

# Mock database simulating transactional records for the agent to query
MOCK_TRANSACTIONS = [
    {"transaction_id": "TXN001", "vendor": "CloudHosting Services", "amount": 12500, "category": "Infrastructure", "status": "Settled"},
    {"transaction_id": "TXN002", "vendor": "SaaSFlow CRM", "amount": 4500, "category": "Software", "status": "Settled"},
    # Simulating a double-billing anomaly (Same vendor, same amount, separate transaction IDs)
    {"transaction_id": "TXN003", "vendor": "Global Logistics Corp", "amount": 32000, "category": "Shipping", "status": "Settled"},
    {"transaction_id": "TXN004", "vendor": "Global Logistics Corp", "amount": 32000, "category": "Shipping", "status": "Pending"}, 
    {"transaction_id": "TXN005", "vendor": "OfficeSupply Ltd", "amount": 1200, "category": "Supplies", "status": "Settled"},
    {"transaction_id": "TXN006", "vendor": "SaaSFlow CRM", "amount": 4500, "category": "Software", "status": "Settled"}
]

@app.route('/', methods=['GET'])
def health_check():
    return jsonify({"status": "FinGuard MCP Bridge is active and online"}), 200

@app.route('/audit', methods=['POST'])
def audit_transactions():
    """
    Exposes a transactional auditing tool to Google Cloud Agent Builder.
    It automatically scans records to identify potential double-billing risks.
    """
    data = request.get_json() or {}
    min_amount = data.get("min_amount", 0)
    
    seen = {}
    duplicates = []
    
    for txn in MOCK_TRANSACTIONS:
        if txn["amount"] >= min_amount:
            # Generate a key using Vendor and Amount to flag potential duplicate billing
            key = (txn["vendor"], txn["amount"])
            if key in seen:
                if seen[key] not in duplicates:
                    duplicates.append(seen[key])
                duplicates.append(txn)
            else:
                seen[key] = txn

    return jsonify({
        "success": True,
        "risk_level": "HIGH" if len(duplicates) > 0 else "LOW",
        "anomalies_found": len(duplicates) // 2,
        "flagged_records": duplicates
    }), 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)