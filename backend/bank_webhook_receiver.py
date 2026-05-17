"""
SafeNest v2.0 — Bank Webhook Receiver (Test)
Example webhook receiver that banks can use to test SafeNest integration
Run this on your bank's server to receive real-time fraud detection notifications
"""

from fastapi import FastAPI, Request, HTTPException, Header
from typing import Optional, Dict, Any
import hmac
import hashlib
import json
from datetime import datetime
import uvicorn

app = FastAPI(
    title="Bank Webhook Receiver",
    description="Example webhook receiver for SafeNest fraud detection notifications"
)

# Store test transactions
received_transactions = []

def verify_signature(payload: str, signature: str, secret: str) -> bool:
    """Verify HMAC-SHA256 signature from SafeNest"""
    expected_signature = hmac.new(
        secret.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected_signature)

@app.post("/webhooks/safenest/transaction")
async def receive_fraud_detection(
    request: Request,
    x_safenest_signature: Optional[str] = Header(None),
    x_safenest_timestamp: Optional[str] = Header(None)
):
    """
    Receive transaction analysis from SafeNest
    
    Headers:
    - X-SafeNest-Signature: HMAC-SHA256 signature
    - X-SafeNest-Timestamp: Unix timestamp of request
    
    Payload:
    {
        "event_type": "transaction_analyzed",
        "transaction_id": "TX_123456",
        "action": "APPROVE" | "OTP_REQUIRED" | "BLOCK" | "FLAG_FOR_REVIEW",
        "risk_level": "LOW" | "MEDIUM" | "HIGH" | "CRITICAL",
        "final_risk_score": 0-100,
        "compliance_status": "COMPLIANT" | "REQUIRES_ATTENTION",
        "ctr_required": bool,
        "sar_required": bool,
        "processing_time_ms": 123,
        "alert_message": "..."
    }
    """
    
    # Get raw body for signature verification
    body = await request.body()
    payload_str = body.decode()
    
    # Verify signature (using test secret)
    WEBHOOK_SECRET = "test-webhook-secret-12345"
    
    if not x_safenest_signature:
        raise HTTPException(status_code=401, detail="Missing X-SafeNest-Signature header")
    
    if not verify_signature(payload_str, x_safenest_signature, WEBHOOK_SECRET):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse payload
    payload = json.loads(payload_str)
    
    # Process transaction
    transaction_data = {
        "received_at": datetime.utcnow().isoformat(),
        "payload": payload
    }
    
    received_transactions.append(transaction_data)
    
    # YOUR BANK'S LOGIC HERE:
    action = payload.get("action")
    transaction_id = payload.get("transaction_id")
    risk_level = payload.get("risk_level")
    
    print(f"\n{'='*70}")
    print(f"🔔 WEBHOOK RECEIVED FROM SAFENEST")
    print(f"{'='*70}")
    print(f"Transaction ID: {transaction_id}")
    print(f"Action: {action}")
    print(f"Risk Level: {risk_level}")
    print(f"Processing Time: {payload.get('processing_time_ms')}ms")
    print(f"Compliance Status: {payload.get('compliance_status')}")
    print(f"Alert Message: {payload.get('alert_message')}")
    print(f"{'='*70}\n")
    
    # Bank's response logic
    if action == "APPROVE":
        bank_action = "EXECUTE_PAYMENT"
        print(f"✅ Bank Action: Execute payment immediately")
    elif action == "OTP_REQUIRED":
        bank_action = "REQUEST_OTP"
        print(f"🔐 Bank Action: Request 2FA from customer")
    elif action == "BLOCK":
        bank_action = "DECLINE_TRANSACTION"
        print(f"🚫 Bank Action: Decline and notify customer")
    elif action == "FLAG_FOR_REVIEW":
        bank_action = "QUEUE_FOR_MANUAL_REVIEW"
        print(f"📋 Bank Action: Queue for compliance team review")
    else:
        bank_action = "UNKNOWN"
    
    # Return acknowledgment
    return {
        "status": "received",
        "transaction_id": transaction_id,
        "bank_action": bank_action,
        "received_at": datetime.utcnow().isoformat()
    }

@app.get("/webhooks/test")
async def test_webhook():
    """Test endpoint to check if receiver is running"""
    return {
        "status": "running",
        "message": "Bank webhook receiver is active",
        "received_transactions_count": len(received_transactions)
    }

@app.get("/webhooks/transactions")
async def get_received_transactions():
    """Get all received transactions (for testing/debugging)"""
    return {
        "count": len(received_transactions),
        "transactions": received_transactions
    }

@app.get("/webhooks/stats")
async def get_webhook_stats():
    """Get webhook statistics"""
    if not received_transactions:
        return {
            "total_received": 0,
            "stats": {
                "APPROVE": 0,
                "OTP_REQUIRED": 0,
                "BLOCK": 0,
                "FLAG_FOR_REVIEW": 0
            }
        }
    
    action_counts = {}
    for tx in received_transactions:
        action = tx["payload"].get("action")
        action_counts[action] = action_counts.get(action, 0) + 1
    
    return {
        "total_received": len(received_transactions),
        "stats": action_counts
    }

@app.delete("/webhooks/transactions")
async def clear_transactions():
    """Clear all received transactions (for testing)"""
    global received_transactions
    received_transactions = []
    return {"status": "cleared"}

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🏦 Bank Webhook Receiver - SafeNest Integration Test")
    print("="*70)
    print("\nEndpoints:")
    print("  POST /webhooks/safenest/transaction  - Receive fraud detection results")
    print("  GET  /webhooks/test                  - Health check")
    print("  GET  /webhooks/transactions          - View received transactions")
    print("  GET  /webhooks/stats                 - View statistics")
    print("  DELETE /webhooks/transactions        - Clear test data")
    print("\nRunning on: http://localhost:9000")
    print("\nTo register this webhook with SafeNest:")
    print("  Bank: Test Bank")
    print("  Webhook URL: http://your-bank-server/webhooks/safenest/transaction")
    print("  Secret: test-webhook-secret-12345")
    print("="*70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=9000)
