# 🔔 SafeNest Webhook Integration Guide

## Overview

Webhooks allow your bank's systems to receive **real-time notifications** of fraud detection results without polling. SafeNest will `POST` transaction analysis results to your registered endpoint.

---

## 🚀 Quick Start

### Step 1: Register Your Webhook Endpoint

**Endpoint:**
```
POST /api/v1/webhooks/register
Authorization: X-API-Key: your-api-key
```

**Request:**
```json
{
  "bank_name": "Your Bank Inc",
  "webhook_url": "https://your-bank-api.com/webhook/safenest",
  "webhook_secret": "your-secret-key-min-32-chars-recommended"
}
```

**Response:**
```json
{
  "status": "success",
  "message": "Webhook registered for Your Bank Inc",
  "webhook_id": 42
}
```

### Step 2: Implement Webhook Receiver

Your bank's server must have an endpoint that receives `POST` requests:

```python
from fastapi import FastAPI, Request, Header
from typing import Optional
import hmac
import hashlib
import json

app = FastAPI()

WEBHOOK_SECRET = "your-secret-key-min-32-chars-recommended"

def verify_signature(payload: str, signature: str) -> bool:
    expected = hmac.new(
        WEBHOOK_SECRET.encode(),
        payload.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

@app.post("/webhook/safenest")
async def receive_fraud_detection(
    request: Request,
    x_safenest_signature: Optional[str] = Header(None),
    x_safenest_timestamp: Optional[str] = Header(None)
):
    # Get raw body
    body = await request.body()
    payload_str = body.decode()
    
    # Verify signature
    if not verify_signature(payload_str, x_safenest_signature):
        return {"error": "Invalid signature"}, 401
    
    # Parse JSON
    payload = json.loads(payload_str)
    
    # Handle transaction
    transaction_id = payload["transaction_id"]
    action = payload["action"]  # APPROVE, OTP_REQUIRED, BLOCK, FLAG_FOR_REVIEW
    risk_level = payload["risk_level"]
    
    print(f"TX {transaction_id}: Action={action}, Risk={risk_level}")
    
    # YOUR LOGIC HERE:
    if action == "APPROVE":
        execute_payment(transaction_id)
    elif action == "OTP_REQUIRED":
        request_otp(transaction_id)
    elif action == "BLOCK":
        decline_payment(transaction_id)
    elif action == "FLAG_FOR_REVIEW":
        queue_for_analyst(transaction_id)
    
    return {"status": "received"}, 200
```

### Step 3: Test with Webhook Receiver

We provide a test webhook receiver to verify your setup:

```bash
# Terminal 1: Start SafeNest
cd backend
python -m uvicorn main:app --reload --port 8000

# Terminal 2: Start test webhook receiver
python bank_webhook_receiver.py
# Running on http://localhost:9000

# Terminal 3: Register the webhook
curl -X POST http://localhost:8000/api/v1/webhooks/register \
  -H "X-API-Key: sk-safenest-demo-key-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "bank_name": "Test Bank",
    "webhook_url": "http://localhost:9000/webhooks/safenest/transaction",
    "webhook_secret": "test-webhook-secret-12345"
  }'

# Terminal 4: Run transaction simulator
python simulator.py
# Select option 4 (Continuous Stream)

# You should see webhooks being received in Terminal 2!
```

---

## 📊 Webhook Payload Format

**Headers:**
```
X-SafeNest-Signature: HMAC-SHA256 signature (verify this!)
X-SafeNest-Timestamp: Unix timestamp of request
Content-Type: application/json
```

**Body:**
```json
{
  "event_type": "transaction_analyzed",
  "timestamp": "2026-05-17T15:30:46.123Z",
  "transaction_id": "TX_20260517_001234",
  "action": "APPROVE",
  "risk_level": "LOW",
  "final_risk_score": 15,
  "compliance_status": "COMPLIANT",
  "ctr_required": false,
  "sar_required": false,
  "processing_time_ms": 234,
  "alert_message": "Transaction approved. Risk score 15/100. Normal merchant and amount."
}
```

**Actions:**
- `APPROVE` → Execute immediately
- `OTP_REQUIRED` → Request 2FA from customer
- `BLOCK` → Decline transaction immediately
- `FLAG_FOR_REVIEW` → Process but mark for analyst

**Risk Levels:**
- `LOW` → Score 0-30
- `MEDIUM` → Score 31-60
- `HIGH` → Score 61-85
- `CRITICAL` → Score 86-100

---

## 🔐 Webhook Security

### Signature Verification (REQUIRED!)

Every webhook includes an `X-SafeNest-Signature` header containing an HMAC-SHA256 signature.

**To verify:**

```python
import hmac
import hashlib

def verify_webhook(payload_string: str, signature: str, secret: str) -> bool:
    expected = hmac.new(
        secret.encode(),
        payload_string.encode(),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(signature, expected)

# Usage
is_valid = verify_webhook(request_body, header_signature, your_secret)
if not is_valid:
    return 401  # Reject
```

**Best Practices:**
1. ✅ Always verify the signature before processing
2. ✅ Use HTTPS endpoints (never HTTP)
3. ✅ Use a strong secret (min 32 characters)
4. ✅ Don't log sensitive data
5. ✅ Return 2xx status to acknowledge receipt
6. ✅ Implement timeout handling (max 10 seconds)

---

## 📈 Webhook Management

### List Registered Webhooks

```bash
curl http://localhost:8000/api/v1/webhooks/list \
  -H "X-API-Key: sk-safenest-demo-key-2026"
```

Response:
```json
[
  {
    "webhook_id": 42,
    "bank_name": "Your Bank Inc",
    "webhook_url": "https://your-bank-api.com/webhook/safenest",
    "is_active": true,
    "success_count": 1250,
    "failure_count": 2,
    "last_triggered": "2026-05-17T15:30:46Z"
  }
]
```

### View Webhook Statistics

```bash
curl http://localhost:8000/api/v1/webhooks/stats \
  -H "X-API-Key: sk-safenest-demo-key-2026"
```

Response:
```json
{
  "total_webhooks": 1,
  "total_success": 1250,
  "total_failure": 2,
  "success_rate": 99.84
}
```

### Deactivate a Webhook

```bash
curl -X DELETE http://localhost:8000/api/v1/webhooks/42 \
  -H "X-API-Key: sk-safenest-demo-key-2026"
```

---

## 🧪 Testing & Debugging

### Enable Webhook Logging

Add to your webhook handler:

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@app.post("/webhook/safenest")
async def receive_webhook(request: Request):
    body = await request.body()
    logger.debug(f"Webhook received: {body.decode()}")
    # ... rest of logic ...
```

### View Test Receiver Stats

```bash
# See all webhooks received
curl http://localhost:9000/webhooks/transactions

# See statistics
curl http://localhost:9000/webhooks/stats

# Clear test data
curl -X DELETE http://localhost:9000/webhooks/transactions
```

---

## 🔄 Webhook Retry Logic

SafeNest attempts to deliver webhooks **once** per transaction analysis.

**If your endpoint is down or returns non-2xx:**
- SafeNest logs the failure
- Check your webhook stats to see failure rates
- Fix your endpoint and re-analyze transactions manually if needed

**Your endpoint should:**
1. Accept the request
2. Verify the signature
3. Process or queue the transaction
4. Return 200-299 status
5. Handle duplicate requests (use transaction_id as key)

---

## 🏦 Production Deployment

### Requirements for Bank Webhook Endpoints

1. **HTTPS Only** - No HTTP endpoints accepted
2. **Valid SSL Certificate** - Must be trusted by certificate authority
3. **Endpoint Monitoring** - Track availability & latency
4. **Error Handling** - Graceful degradation if SafeNest is down
5. **Logging** - Maintain audit trail of all transactions
6. **Backup Systems** - Fallback if webhook fails

### Recommended Architecture

```
┌─────────────────────────────────────────┐
│  SafeNest (Fraud Detection)             │
│  Sends webhook to Bank endpoint         │
└──────────────┬──────────────────────────┘
               │ HTTPS POST
               │ (with signature)
               ▼
┌──────────────────────────────────────────┐
│  Bank Webhook Receiver (Load Balancer)   │
│  Verifies signature                      │
│  Routes to processing queue              │
└──────────────┬───────────────────────────┘
               │
        ┌──────┴──────┐
        ▼             ▼
    ┌────────┐   ┌────────┐
    │Handler │   │Handler │
    │1       │   │2       │
    └────────┘   └────────┘
        │             │
        └──────┬──────┘
               ▼
        ┌─────────────┐
        │  Database   │
        │  (Decision) │
        └─────────────┘
```

---

## 📞 Support & Troubleshooting

### Webhook Not Receiving Events?

1. ✅ Check webhook is registered:
   ```bash
   curl http://localhost:8000/api/v1/webhooks/list \
     -H "X-API-Key: your-api-key"
   ```

2. ✅ Check webhook is active:
   - Status should be `"is_active": true`

3. ✅ Check failure rate:
   ```bash
   curl http://localhost:8000/api/v1/webhooks/stats \
     -H "X-API-Key: your-api-key"
   ```

4. ✅ Verify signature verification:
   - Implement test logging to see signature verification pass/fail

5. ✅ Check endpoint is HTTPS:
   - SafeNest rejects HTTP endpoints for production

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| 401 Signature error | Wrong secret | Verify secret matches in registration |
| Timeout errors | Endpoint too slow | Optimize webhook handler (< 5s) |
| SSL certificate error | Invalid certificate | Renew certificate |
| High failure rate | Endpoint down | Check server logs and health |

---

## 🔧 Advanced: Custom Webhook Triggers

You can configure which events trigger webhooks:

```python
# Register with specific events
curl -X POST http://localhost:8000/api/v1/webhooks/register \
  -H "X-API-Key: your-api-key" \
  -H "Content-Type: application/json" \
  -d '{
    "bank_name": "Bank",
    "webhook_url": "https://...",
    "webhook_secret": "...",
    "events": ["transaction_analyzed", "transaction_escalated"]
  }'
```

**Available Events:**
- `transaction_analyzed` - All transactions analyzed
- `transaction_escalated` - High-risk transactions only
- `ctr_filed` - Currency Transaction Report filed
- `sar_filed` - Suspicious Activity Report filed

---

## ✅ Checklist for Bank Integration

- [ ] Webhook endpoint implemented and tested locally
- [ ] HTTPS enabled with valid certificate
- [ ] Signature verification implemented
- [ ] Signature verification tested with test receiver
- [ ] Webhook registered with SafeNest
- [ ] Transaction simulator sending webhooks successfully
- [ ] Production webhook URL registered
- [ ] Failure handling and retry logic implemented
- [ ] Logging and monitoring configured
- [ ] Load testing completed (1000+ webhooks/minute)
- [ ] Team trained on webhook handling
- [ ] Incident response plan documented

---

For more information, see [REAL_TIME_INTEGRATION.md](REAL_TIME_INTEGRATION.md)
