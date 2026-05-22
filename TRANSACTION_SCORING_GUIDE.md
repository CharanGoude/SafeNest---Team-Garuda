# SafeNest Transaction Risk Scoring Flow

## 1️⃣ First Transaction (Baseline)
```
User makes first transaction
    ↓
No baseline found in DB
    ↓
✅ Auto-APPROVED (Risk: 10%)
    ↓
Baseline stored in database
    ↓
Next transactions will compare to this
```

## 2️⃣ Subsequent Transactions (Comparison)
```
User makes 2nd+ transaction
    ↓
Coordinator retrieves baseline
    ↓
Compare 8 parameters:
  ├─ Location (Country)      → +50% if different
  ├─ Device ID               → +40% if different
  ├─ IP Address              → +35% if different
  ├─ Amount (vs baseline)    → +15-50% if higher
  ├─ Velocity (time gap)     → +15-40% if rapid
  ├─ Merchant Name           → +30% if different
  ├─ Merchant Category       → +20% if different
  └─ Multiple changes        → +10% penalty per extra param
    ↓
Calculate: Base(10%) + Deviations (capped at 100%)
    ↓
Decision based on Risk Score
```

## 3️⃣ Risk Score Decision Matrix

| Score | Action | Risk Level | User Experience |
|-------|--------|-----------|-----------------|
| 0-29 | ✅ APPROVE | LOW | Transaction goes through |
| 30-49 | 🚩 FLAG_FOR_REVIEW | MEDIUM | Manual analyst review |
| 50-64 | 🔐 REQUIRE_OTP | HIGH | Customer must enter OTP |
| 65-74 | ⏸️ HOLD_TRANSACTION | HIGH | Transaction held, verification needed |
| 75-89 | ❄️ FREEZE_ACCOUNT | CRITICAL | Account frozen, security alert sent |
| 90-100 | 🛑 BLOCK | CRITICAL | Transaction rejected immediately |

## 4️⃣ Scoring Examples

### Example A: Low Risk (Same as Baseline)
```
Baseline:     Coca-Cola, Amount: $50, Location: Mumbai, Device: iPhone
Current Tx:   Coca-Cola, Amount: $45, Location: Mumbai, Device: iPhone

Score = 10 (base) + 0 = 10 ✅ APPROVE
```

### Example B: Medium Risk (Location + Amount Change)
```
Baseline:     Amazon, Amount: $100, Location: India, Device: iPhone, IP: 192.168.1.1
Current Tx:   Amazon, Amount: $200, Location: USA, Device: iPhone, IP: 91.108.1.1

Score = 10 + 0 + 50 (location) + 25 (2x amount) + 35 (IP) = 120 → 100 (CAPPED)
Action = 🛑 BLOCK (≥90)
```

### Example C: OTP Trigger (Multiple Small Changes)
```
Baseline:     Starbucks, $30, India, iPhone_14, 192.168.1.1
Current Tx:   Starbucks, $40, India, Samsung_S23, 192.168.1.50

Score = 10 + 0 + 0 + 15 (1.33x amount) + 40 (device) = 65
Action = ⏸️ HOLD_TRANSACTION (65-74)
```

### Example D: OTP Trigger (Location + Device + IP)
```
Baseline:     Netflix, $15, India, iPhone, 192.168.1.1
Current Tx:   Netflix, $15, USA, Unknown_Device, 185.220.1.1

Score = 10 + 50 (location) + 40 (device) + 35 (IP) = 135 → 100 (CAPPED)
Action = 🛑 BLOCK (≥90)
```

### Example E: OTP Sweet Spot
```
Baseline:     Food Order, $20, India, iPhone, 192.168.1.1
Current Tx:   Food Order, $35, India, iPhone, 192.168.1.50

Score = 10 + 0 + 0 + 0 + 15 (1.75x amount) + 0 = 25
Action = ✅ APPROVE (<30)

Now transaction 3:
Baseline:     Food Order, $20, India, iPhone, 192.168.1.1
Current Tx:   Food Order, $45, India, Samsung, 192.168.2.1

Score = 10 + 0 + 40 (device) + 0 + 25 (2.25x amount) + 0 = 75
Action = ❄️ FREEZE (75-89)
```

## 5️⃣ OTP Requirement Rules

**OTP is triggered when:**
- Risk score 50-64
- Common triggers:
  - ✓ Location change + device change
  - ✓ Amount increase (>2x) + IP change
  - ✓ New device + different merchant + rapid transaction
  - ✓ Any 2+ parameters changed from baseline

**OTP is NOT triggered when:**
- All parameters match baseline (score 10)
- Single small change (score <50)
- BLOCK/FREEZE triggered (security hold instead)

## 6️⃣ Secondary Actions by Decision

```
APPROVE (Low Risk)
  └─ [None]

FLAG_FOR_REVIEW
  └─ QUEUE_FOR_ANALYST_REVIEW

HOLD_TRANSACTION  
  └─ [None - manual verification needed]

REQUIRE_OTP
  └─ SEND_OTP_TO_CUSTOMER

FREEZE_ACCOUNT
  ├─ NOTIFY_SECURITY_TEAM
  └─ SEND_SMS_ALERT_TO_CUSTOMER

BLOCK
  ├─ NOTIFY_SECURITY_TEAM
  ├─ SEND_SMS_ALERT_TO_CUSTOMER
  └─ ESCALATE_TO_COMPLIANCE_OFFICER
```

## 7️⃣ Database Schema

### Baseline Transactions Table
```sql
CREATE TABLE baseline_transactions (
    id INTEGER PRIMARY KEY,
    user_id TEXT,
    account_number TEXT,
    amount REAL,
    location_country TEXT,
    location_city TEXT,
    merchant_name TEXT,
    merchant_category TEXT,
    device_id TEXT,
    ip_address TEXT,
    timestamp REAL,
    UNIQUE(user_id, account_number)
);
```

One baseline per user/account combination.

## 8️⃣ API Response Structure

```json
{
  "transaction_id": "ABC12345",
  "action": "REQUIRE_OTP",
  "risk_level": "HIGH",
  "final_risk_score": 55,
  "alert_message": "OTP verification required. Risk score 55/100.",
  "comparison_indicators": [
    "Country location changed: IN → US (+50%)",
    "New IP address: 192.168.1.1 → 91.108.1.1 (+35%)"
  ],
  "parameter_changes": [
    "Location: IN → US (+50%)",
    "IP Address: 192.168.1.1 → 91.108.1.1 (+35%)"
  ],
  "blockchain_hash": "a3c9d2e...",
  "secondary_actions": ["SEND_OTP_TO_CUSTOMER"]
}
```

---

## Flow Summary
1. **First transaction** → Baseline stored, auto-approved
2. **All future transactions** → Compared to baseline
3. **Risk calculated** → Base 10% + parameter deviations
4. **Action triggered** → Based on risk score threshold
5. **Secondary actions** → Alerts, OTP, escalations as needed
6. **Blockchain recorded** → Immutable transaction history
