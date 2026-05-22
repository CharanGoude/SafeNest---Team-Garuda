# 🛡️ SafeNest v2.0 — Baseline-Comparison Fraud Detection

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

## 🚀 Architecture - Coordinator Agent (v2.0)

### ✨ Key Features

- ✅ **Coordinator Agent** — Baseline-comparison transaction scoring
- ✅ **Removed Auditor** — KYC handled by banks directly
- ✅ **Progressive Risk Scoring** — Each parameter deviation increases risk
- ✅ **OTP at 50-64% Risk** — Smart authentication for medium-risk transactions
- ✅ **SQLite Database** — Persistent baseline storage & transaction history
- ✅ **Blockchain Ledger** — Immutable audit trail for compliance
- ✅ **API Key Authentication** — Production-ready security
- ✅ **Real-Time Alerts** — WebSocket notifications for high-risk transactions

### 🎯 Risk Decision Thresholds

| Score | Action | Risk Level | User Experience |
|-------|--------|-----------|-----------------|
| 0-29 | ✅ APPROVE | LOW | Instant approval |
| 30-49 | 🚩 FLAG_FOR_REVIEW | MEDIUM | Analyst review |
| 50-64 | 🔐 REQUIRE_OTP | HIGH | OTP verification |
| 65-74 | ⏸️ HOLD_TRANSACTION | HIGH | Hold for review |
| 75-89 | ❄️ FREEZE_ACCOUNT | CRITICAL | Account frozen |
| 90-100 | 🛑 BLOCK | CRITICAL | Transaction blocked |

### 📊 Parameter Risk Scoring

Each parameter deviation from baseline increases risk:

| Parameter | Risk Increase |
|-----------|---------------|
| Location Country Change | +50% |
| Device ID Change | +40% |
| IP Address Change | +35% |
| Amount 2x-3x Baseline | +25% |
| Amount 3x-5x Baseline | +35% |
| Amount 5x+ Baseline | +50% |
| Rapid Transaction (<3 min) | +40% |
| Rapid Transaction (<10 min) | +25% |
| Rapid Transaction (<30 min) | +15% |
| Merchant Name Change | +30% |
| Merchant Category Change | +20% |
| Multiple Parameters (>2) | +10% penalty per change |
| **Base Risk Score** | **10%** |

---

## 💡 How It Works

### 1️⃣ First Transaction (Baseline)
```
User makes first transaction
  ↓
✅ Auto-APPROVED (Risk: 10%)
  ↓
Baseline saved to database
```

### 2️⃣ Subsequent Transactions (Comparison)
```
Transaction received
  ↓
Retrieve baseline from database
  ↓
Compare 8 parameters:
  • Location (Country)
  • Device ID
  • IP Address
  • Amount (vs baseline)
  • Velocity (time gap)
  • Merchant Name
  • Merchant Category
  • Multiple changes penalty
  ↓
Calculate: Base 10% + Deviations (max 100%)
  ↓
Decision based on risk score:
  • 50-64 → OTP required
  • 65-74 → Hold transaction
  • 75-89 → Freeze account
  • 90-100 → Block immediately
```

### 🔐 OTP Trigger Examples

**OTP is triggered when risk score reaches 50-64:**

```
Example 1: Location change only
  Risk = 10 (base) + 50 (location) = 60 → REQUIRE_OTP ✓

Example 2: Device change only
  Risk = 10 + 40 (device) = 50 → REQUIRE_OTP ✓

Example 3: Amount 2x + Merchant change
  Risk = 10 + 25 (amount) + 20 (merchant) = 55 → REQUIRE_OTP ✓

Example 4: Location + Device (too high)
  Risk = 10 + 50 + 40 = 100 (capped) → BLOCK ✗

Example 5: Multiple small changes
  Risk = 10 + 15 (amount) + 40 (device) = 65 → HOLD ✗
```

---

## ⚡ Quick Start

### Terminal 1 — Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

✅ Backend: http://localhost:8000
✅ API Docs: http://localhost:8000/docs
✅ Health: http://localhost:8000/health

### Terminal 2 — Frontend
```bash
cd frontend
npm install
npm run dev
```

✅ Dashboard: http://localhost:3000 (or auto-detected port)

### Terminal 3 — Simulate Transactions
```bash
cd backend
python simulator.py
```

Test different scenarios:
- ✅ **Safe transaction** — All parameters match → APPROVE
- ✅ **Medium risk** — Location change → OTP required
- ✅ **High risk** — Multiple changes → FREEZE/BLOCK

---

## 📁 Project Structure

```
SafeNest/
├── backend/
│   ├── agents/
│   │   ├── __init__.py
│   │   ├── coordinator.py        ← NEW: Baseline comparison agent
│   │   ├── response.py           ← Updated: New thresholds
│   │   ├── sentry.py             ← Fraud detection (optional)
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── database.py       ← Updated: baseline_transactions table
│   ├── main.py                   ← Updated: New pipeline
│   ├── models.py
│   ├── requirements.txt
│   └── simulator.py
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx
│   │   │   ├── TransactionsPage.jsx
│   │   │   ├── AnalyzePage.jsx
│   │   │   └── BlockchainPage.jsx
│   │   ├── utils/
│   │   │   └── api.js
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── vite.config.js
│   ├── package.json
│   └── index.html
├── COORDINATOR_AGENT_CHANGES.md    ← Implementation details
├── TRANSACTION_SCORING_GUIDE.md    ← Scoring logic
├── OTP_TRIGGER_RULES.md            ← OTP examples
├── IMPLEMENTATION_CHECKLIST.md
└── README.md
```

---

## 📊 API Endpoints

### Core Transaction Analysis
```http
POST /api/v1/analyze
X-API-Key: sk-safenest-demo-key-2026

{
  "user_id": "user_rahul_k",
  "account_number": "ACC123456",
  "amount": 2500.0,
  "location_country": "US",
  "location_city": "New York",
  "device_id": "iPhone_14",
  "ip_address": "185.220.1.1",
  "merchant_name": "Amazon",
  "merchant_category": "RETAIL",
  "account_age_days": 730,
  "user_avg_transaction": 800.0,
  "previous_transaction_minutes_ago": 120
}
```

**Response:**
```json
{
  "transaction_id": "ABC12345",
  "action": "REQUIRE_OTP",
  "risk_level": "HIGH",
  "final_risk_score": 60,
  "alert_message": "OTP verification required. Risk score 60/100.",
  "comparison_indicators": [
    "Country location changed: IN → US (+50%)",
    "Transaction amount 2.5x baseline: $800 → $2500 (+25%)"
  ],
  "parameter_changes": [
    "Location: IN → US (+50%)",
    "Amount: $800 → $2500 (2.5x, +25%)"
  ]
}
```

### Other Endpoints
```http
GET /api/v1/transactions              # List all transactions
GET /api/v1/transactions/{id}         # Transaction details
GET /api/v1/stats                     # Dashboard statistics
GET /api/v1/blockchain                # Blockchain ledger
GET /health                            # System health
POST /api/v1/simulate?count=5         # Test simulator
```

---

## 🗄️ Database Schema

### New Table: baseline_transactions
```sql
user_id             TEXT (Primary Key Part 1)
account_number      TEXT (Primary Key Part 2)
amount              REAL
location_country    TEXT
location_city       TEXT
merchant_name       TEXT
merchant_category   TEXT
device_id           TEXT
ip_address          TEXT
timestamp           REAL
```

Each user/account combination has ONE baseline (first transaction).

---

## 🔒 Security & Compliance

- ✅ **API Key Authentication** — All requests require valid API key
- ✅ **Baseline Verification** — Prevents account takeover via profile switching
- ✅ **Progressive Controls** — OTP → Hold → Freeze → Block
- ✅ **Blockchain Audit Trail** — Immutable record of all decisions
- ✅ **Real-Time Alerts** — Security team notified of suspicious activity
- ✅ **Secondary Actions** — Auto-escalation to compliance officers

---

## 📝 Documentation

- **[COORDINATOR_AGENT_CHANGES.md](COORDINATOR_AGENT_CHANGES.md)** — Implementation overview
- **[TRANSACTION_SCORING_GUIDE.md](TRANSACTION_SCORING_GUIDE.md)** — Detailed scoring examples
- **[OTP_TRIGGER_RULES.md](OTP_TRIGGER_RULES.md)** — OTP trigger scenarios
- **[IMPLEMENTATION_CHECKLIST.md](IMPLEMENTATION_CHECKLIST.md)** — Deployment checklist

---

## 🚀 Deployment

### Local Development
```bash
# Backend
cd backend && uvicorn main:app --reload

# Frontend (in another terminal)
cd frontend && npm run dev
```

### Production
```bash
# Backend
gunicorn main:app --workers 4

# Frontend
npm run build
serve dist/
```

---

## 📞 API Keys for Testing

| Bank | API Key | Status |
|------|---------|--------|
| Demo Bank | `sk-safenest-demo-key-2026` | ✅ Active |
| Test Integration | `sk-safenest-test-key-2026` | ✅ Active |

---

## 🎯 Version Info

- **Current Version:** 2.0.0
- **Architecture:** Coordinator Agent (Baseline-Comparison)
- **Database:** SQLite
- **Frontend:** React + Vite
- **Backend:** FastAPI + Python 3.10+
- **Last Updated:** May 2026

---

## ✅ Implementation Status

- ✅ Coordinator Agent implemented
- ✅ Baseline-comparison scoring
- ✅ OTP trigger logic (50-64 range)
- ✅ Risk thresholds configured
- ✅ Database schema updated
- ✅ API endpoints working
- ✅ Frontend integration ready
- ✅ Documentation complete

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
