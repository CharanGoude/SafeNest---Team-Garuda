# 🛡️ SafeNest v2.0 — Autonomous Fraud Detection & Compliance System

**Team Garuda | Dr MGR Educational And Research Institute**
**Virtusa Jatayu Season 5 — Stage 3**

---

## 👥 Team

| Name | Role | Email |
|------|------|-------|
| E. Charan Goud (Team Lead) | Frontend & Architecture | charangoude@gmail.com |
| I. Haridhar | Backend & AI Agents | illuriharidhar@gmail.com |
| D. Vishnuvardhan Reddy | Compliance & Blockchain | vishnuvardhanr257@gmail.com |

---

## 🚀 What's New in v2.0

- ✅ **Removed Coordinator Agent** — direct 3-agent pipeline (Sentry → Auditor → Response)
- ✅ **Real SQLite database** — persistent storage, not in-memory
- ✅ **API Key authentication** — production-ready security
- ✅ **Parallel agent execution** — Sentry & Auditor run simultaneously
- ✅ **CTR/SAR auto-filing** — full regulatory compliance logic
- ✅ **Clean bank integration** — one POST call, standard JSON
- ✅ **Swagger API docs** — auto-generated at /docs

---

## ⚡ Quick Start

### Terminal 1 — Backend
```bash
cd backend
pip install -r requirements.txt

# Optional: add Gemini API key for AI reasoning
cp .env.example .env
# Edit .env and add your GOOGLE_API_KEY

uvicorn main:app --reload --port 8000
```

✅ Backend: http://localhost:8000
✅ API Docs: http://localhost:8000/docs

### Terminal 2 — Frontend
```bash
cd frontend
npm install
npm run dev
```

✅ Dashboard: http://localhost:3000 (or 3001 if 3000 is in use)
### Terminal 3 — Transaction Simulator (Test Real-Time Flow)
```bash
cd backend
python simulator.py
```

This lets you test fraud detection without needing a real bank:
- Simulate normal transactions (low risk - APPROVE)
- Simulate high-risk transactions (medium risk - OTP_REQUIRED)
- Simulate fraudulent transactions (high risk - BLOCK)
- Simulate continuous transaction stream (watch dashboard update in real-time)

### Terminal 4 — Bank Webhook Receiver (Optional - Test Integration)
```bash
cd backend
python bank_webhook_receiver.py
```

This webhook receiver helps test how banks receive fraud detection notifications:
- Verify webhook signatures
- View received transaction results
- Test end-to-end integration before production deployment
---

## 🔧 Recent Fixes & Updates (v2.0.1)

### Import Path Resolution
- **Backend**: Fixed module import path for database (`agents/db/database.py`)
  - Created `agents/db/__init__.py` to make it a proper Python package
  - Updated import in `main.py` from `from db.database import db` to `from agents.db.database import db`

- **Frontend**: Consolidated API utilities
  - Moved `/frontend/utils/api.js` to `/frontend/src/utils/api.js` for proper module resolution
  - Updated all component imports to use correct relative paths:
    - `App.jsx`: `./utils/api`
    - Page components: `../utils/api`

### Build & Run Status
- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:3001 (auto-detected available port)
- ✅ All module imports resolved
- ✅ Auto-reload enabled for both services

---

## 🚀 Real-Time Fraud Detection (v2.0 Core Feature)

### How It Works (Invisible to Customer)

```
Customer Mobile → Bank System → SafeNest API (< 500ms) → Decision → Dashboard
```

1. **Customer initiates transaction on mobile** (doesn't know fraud detection is happening)
2. **Bank receives request** and immediately calls SafeNest API
3. **SafeNest analyzes in real-time**:
   - Sentry Agent: Device fingerprinting, geolocation, IP reputation
   - Auditor Agent: Behavioral patterns, amount anomalies, merchant validation
   - Response Agent: Compliance check, final decision
4. **Decision returned to bank** within 500ms:
   - ✅ `APPROVE` - Execute immediately
   - 🔐 `OTP_REQUIRED` - Request 2FA from customer
   - 🚫 `BLOCK` - Decline transaction
   - 📋 `FLAG_FOR_REVIEW` - Process but mark for analyst
5. **Dashboard shows real-time updates** via WebSocket
6. **Bank knows everything** - full transaction audit trail

See [REAL_TIME_INTEGRATION.md](REAL_TIME_INTEGRATION.md) for complete architecture & API documentation.

---

## 🔔 Bank Webhook Integration (v2.0.1 NEW)

Banks can now register webhook endpoints to receive **real-time fraud detection notifications**:

```bash
# Register your bank's webhook endpoint
curl -X POST http://localhost:8000/api/v1/webhooks/register \
  -H "X-API-Key: sk-safenest-demo-key-2026" \
  -H "Content-Type: application/json" \
  -d '{
    "bank_name": "Your Bank",
    "webhook_url": "https://your-bank-api.com/webhook/safenest",
    "webhook_secret": "your-secret-key"
  }'
```

**What Banks Get:**
- Real-time POST request for each analyzed transaction
- HMAC-SHA256 signature verification
- Transaction decision (APPROVE/OTP_REQUIRED/BLOCK/FLAG_FOR_REVIEW)
- Risk level and compliance status
- < 1 second end-to-end latency

**Webhook Security:**
- ✅ HMAC-SHA256 signature verification required
- ✅ HTTPS only for production
- ✅ Automatic retry on failure
- ✅ Audit logging of all webhooks

See [WEBHOOK_INTEGRATION.md](WEBHOOK_INTEGRATION.md) for complete webhook guide, examples, and best practices.

---

## 📁 New Files (v2.0.1)

---

## 📁 New Files (v2.0.1)

**Real-Time Integration:**
- `REAL_TIME_INTEGRATION.md` — Complete architecture & data flow diagrams
- `WEBHOOK_INTEGRATION.md` — Bank webhook integration guide

**Transaction Simulation:**
- `backend/simulator.py` — Test real-time fraud detection without needing a real bank

**Webhook System (Production-Ready):**
- `backend/webhook_manager.py` — Webhook registration & management
- `backend/webhook_sender.py` — Async webhook broadcasting to banks
- `backend/webhook_api.py` — FastAPI endpoints for webhook management
- `backend/bank_webhook_receiver.py` — Test receiver for banks to verify integration

---

Just **one API call** added to your existing transaction flow:

```python
import requests

def process_payment(transaction):
    # Send to SafeNest for analysis
    result = requests.post(
        "https://your-safenest-server/api/v1/analyze",
        headers={"X-API-Key": "your-bank-api-key"},
        json={
            "account_number":    transaction.account_number,
            "user_id":           transaction.user_id,
            "amount":            transaction.amount,
            "merchant_name":     transaction.merchant,
            "location_country":  transaction.country,
            "device_id":         transaction.device_id,
            "ip_address":        transaction.ip_address,
            "is_new_device":     transaction.is_new_device,
            "account_age_days":  transaction.account_age_days,
            "user_avg_transaction": transaction.avg_amount,
        }
    ).json()

    # Act on SafeNest's decision
    action = result["action"]

    if action == "APPROVE":
        execute_payment(transaction)

    elif action == "REQUIRE_OTP":
        send_otp_to_customer(transaction)

    elif action == "FLAG_FOR_REVIEW":
        notify_analyst(transaction)

    elif action == "FREEZE_ACCOUNT":
        freeze_account(transaction.account_number)
        notify_security_team(transaction)

    elif action == "BLOCK":
        block_transaction(transaction)
        notify_security_team(transaction)

    return result
```

**Compatible with:** Finacle, TCS BaNCS, Temenos T24, Oracle FLEXCUBE, any UPI stack.

---

## 🤖 3-Agent Pipeline

```
Transaction Input
      │
      ├──────────────────────────────────┐
      ▼                                  ▼
┌───────────────┐              ┌─────────────────┐
│  Sentry Agent │              │  Auditor Agent  │
│               │              │                 │
│ Fraud Pattern │              │  KYC · AML      │
│ Detection     │              │  Watchlist      │
│ Gemini AI     │              │  CTR/SAR Filing │
│ + Rules       │              │  Gemini AI      │
│               │              │  + Rules        │
│ Score: 0-100  │              │ COMPLIANT/FLAG  │
└───────┬───────┘              └────────┬────────┘
        │                              │
        └──────────────┬───────────────┘
                       ▼
              ┌────────────────┐
              │ Response Agent │
              │                │
              │ Combines Scores│
              │ 60% + 40%      │
              │ Decides Action │
              │ Writes Block   │
              └───────┬────────┘
                      │
          ┌───────────┼───────────┐──────────┐
          ▼           ▼           ▼          ▼
       APPROVE    REQUIRE_OTP  FREEZE     BLOCK
```

---

## 🎯 Risk Score → Action Mapping

| Score | Action | What Happens |
|-------|--------|-------------|
| 0–29  | APPROVE | Transaction processed normally |
| 30–49 | FLAG_FOR_REVIEW | Held for analyst review |
| 50–69 | REQUIRE_OTP | OTP sent to customer's phone |
| 70–89 | FREEZE_ACCOUNT | Account frozen + security alerted |
| 90–100| BLOCK | Transaction blocked + SAR filed |

---

## 📡 API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| GET | `/health` | None | System health check |
| POST | `/api/v1/analyze` | API Key | Analyze transaction |
| GET | `/api/v1/transactions` | API Key | Transaction history |
| GET | `/api/v1/transactions/{id}` | API Key | Single transaction |
| GET | `/api/v1/stats` | API Key | Dashboard statistics |
| GET | `/api/v1/blockchain` | API Key | Compliance ledger |
| POST | `/api/v1/simulate` | API Key | Generate test data |
| WS | `/ws` | None | Real-time alerts |

**Demo API Key:** `sk-safenest-demo-key-2026`

---

## 📁 Project Structure

```
SafeNest/
├── backend/
│   ├── main.py               ← FastAPI app + all routes
│   ├── models.py             ← Pydantic data models
│   ├── requirements.txt
│   ├── .env.example
│   ├── agents/
│   │   ├── sentry.py         ← Fraud detection (Gemini AI + rules)
│   │   ├── auditor.py        ← KYC/AML/compliance
│   │   └── response.py       ← Action engine + blockchain
│   └── db/
│       └── database.py       ← SQLite with production-ready schema
└── frontend/
    ├── src/
    │   ├── App.jsx            ← Layout + sidebar + WebSocket
    │   ├── utils/api.js       ← Centralized API client
    │   ├── components/UI.jsx  ← Shared UI components
    │   └── pages/
    │       ├── Dashboard.jsx
    │       ├── AnalyzePage.jsx
    │       ├── TransactionsPage.jsx
    │       └── BlockchainPage.jsx
    ├── package.json
    └── vite.config.js
```

---

## 🔐 Security

- API Key authentication on all endpoints
- TLS 1.3 for data in transit (production)
- AES-256 for database encryption (production)
- SHA-256 hashing for blockchain immutability
- No raw PII stored — only behavioral attributes

---

## 🏗️ Production Deployment

### 🚀 Quick Deploy to AWS EC2 (Recommended for Production)

**Fastest way to get SafeNest live with SSL, Nginx, and automated backups:**

```bash
# 1. Launch EC2 instance (Ubuntu 22.04 LTS, t3.medium)
# 2. SSH into instance
ssh -i safenest-key.pem ubuntu@<PUBLIC_IP>

# 3. Run automated setup script (15 minutes)
curl -O https://raw.githubusercontent.com/CharanGoude/SafeNest---Team-Garuda/main/setup-safenest-aws.sh
chmod +x setup-safenest-aws.sh
./setup-safenest-aws.sh safenest-garuda.com your-email@example.com

# 4. Configure domain DNS to point to EC2 public IP
# 5. Access dashboard at https://safenest-garuda.com
```

**What's Included:**
- ✅ Python 3.10 + Node.js 18
- ✅ SSL certificate (Let's Encrypt)
- ✅ Nginx reverse proxy with HTTPS
- ✅ Supervisor process manager
- ✅ Automated daily backups
- ✅ UFW firewall configured
- ✅ Production-ready logging

**Cost Estimate:**
- t3.medium: ~$25/month
- Domain: $10-15/year
- SSL: Free (Let's Encrypt)

📖 **Full Guide:** See [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md)
📋 **Quick Checklist:** See [AWS_DEPLOYMENT_CHECKLIST.md](AWS_DEPLOYMENT_CHECKLIST.md)

---

### Alternative: Render.com (Backend — Free Tier)

**Build:** `pip install -r requirements.txt`
**Start:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
**Env:** `GOOGLE_API_KEY=your_key`

### Alternative: Vercel (Frontend — Free Tier)

**Framework:** Vite
**Env:** 
```
VITE_API_URL=https://your-render-url.onrender.com
VITE_API_KEY=sk-safenest-demo-key-2026
```
