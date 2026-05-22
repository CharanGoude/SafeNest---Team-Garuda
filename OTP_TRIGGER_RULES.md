# SafeNest OTP Trigger Rules - Detailed Breakdown

## OTP is Required When: Risk Score 50-64

OTP (One-Time Password) verification is triggered for transactions with risk scores between **50-64**, which falls in the **HIGH** risk category but doesn't warrant freezing the account.

## How Risk Score Reaches 50-64 Range

### Scenario 1: Location Change (50%) + Device Change (40%) - Too High
```
Calculation: 10 (base) + 50 (location) + 40 (device) = 100
Risk Score: 100 (CAPPED)
Action: BLOCK (not OTP, because 100 ≥ 90)
```

### Scenario 2: Location Change (50%) Only - Too High
```
Calculation: 10 (base) + 50 (location) = 60
Risk Score: 60
Action: ✅ REQUIRE_OTP (50 ≤ 60 ≤ 64)
```

### Scenario 3: Amount Increase (25%) + Device Change (40%) - Just Right
```
Calculation: 10 (base) + 25 (amount 2x) + 40 (device) = 75
Risk Score: 75
Action: FREEZE_ACCOUNT (not OTP, because 75 ≥ 75)
```

### Scenario 4: Amount Increase (25%) + IP Change (35%) - Too High
```
Calculation: 10 (base) + 25 (amount) + 35 (IP) = 70
Risk Score: 70
Action: HOLD_TRANSACTION (65 ≤ 70 ≤ 74)
```

### Scenario 5: Rapid Transaction (40%) + Merchant Change (30%) - Too High
```
Calculation: 10 (base) + 40 (rapid) + 30 (merchant) = 80
Risk Score: 80
Action: FREEZE_ACCOUNT (80 ≥ 75)
```

### Scenario 6: Amount Increase (15%) + Device Change (40%)
```
Calculation: 10 (base) + 15 (amount 1.5x) + 40 (device) = 65
Risk Score: 65
Action: HOLD_TRANSACTION (65 ≤ 65 ≤ 74)
```

### Scenario 7: Amount Increase (25%) + Merchant Category Change (20%)
```
Calculation: 10 (base) + 25 (amount) + 20 (category) = 55
Risk Score: 55
Action: ✅ REQUIRE_OTP (50 ≤ 55 ≤ 64)
```

### Scenario 8: Location Change (50%) + No Other Changes = OTP
```
Baseline:
- Location: India
- Device: iPhone
- Amount: $100
- Merchant: Amazon
- IP: 192.168.1.1

Current Transaction:
- Location: USA ← CHANGED
- Device: iPhone
- Amount: $100
- Merchant: Amazon
- IP: 192.168.1.1

Calculation: 10 (base) + 50 (location changed) = 60
Risk Score: 60
Action: ✅ REQUIRE_OTP (50 ≤ 60 ≤ 64)
Alert: "OTP verification required. Risk score 60/100."
```

## Real-World OTP Trigger Examples

### ✅ Example 1: International Travel (SHOULD TRIGGER OTP)
```
Day 1 - Baseline Transaction (Home):
- User: Rahul
- Amount: $50
- Location: Mumbai, India
- Device: iPhone 14
- IP: 192.168.1.100
- Merchant: Starbucks
Risk: 10 → APPROVE ✓

Day 5 - Transaction from USA:
- User: Rahul
- Amount: $50
- Location: New York, USA ← LOCATION CHANGED (+50%)
- Device: iPhone 14 (same roaming)
- IP: 185.220.50.200 (new in USA) ← IP CHANGED (+35%)
- Merchant: Starbucks
Risk: 10 + 50 = 60 → REQUIRE_OTP ✓
Alert: "OTP required. Detected international transaction."
```

### ✅ Example 2: New Device + Increased Amount (SHOULD TRIGGER OTP)
```
Baseline:
- Amount: $200/month average
- Device: iPhone (registered)
- Merchant: Flipkart
Risk: 10

Current Transaction:
- Amount: $500 (2.5x) ← AMOUNT (+25%)
- Device: Unknown_Tablet ← DEVICE CHANGED (+40%)
- Merchant: Flipkart
Risk: 10 + 25 + 40 = 75 → FREEZE (NOT OTP, too high)
```

### ✅ Example 3: Rapid Transactions + Merchant Change (SHOULD TRIGGER OTP)
```
Transaction 1:
- Amount: $100
- Time: 2:00 PM
- Device: iPhone
- Location: Delhi
Risk: 10

Transaction 2 (3 minutes later):
- Amount: $100
- Time: 2:03 PM ← RAPID (+40%)
- Device: iPhone
- Location: Delhi
- Merchant: Different ← MERCHANT CHANGED (+30%)
Risk: 10 + 40 + 30 = 80 → FREEZE (NOT OTP)

Better scenario:
- Rapid only: 10 + 40 = 50 → REQUIRE_OTP ✓
- Rapid + Merchant: 10 + 40 + 30 = 80 → FREEZE
```

### ✅ Example 4: Amount Increase Only (SHOULD NOT TRIGGER OTP - TOO LOW)
```
Baseline:
- Amount: $50
- Location: India
- Device: iPhone

Current:
- Amount: $75 (1.5x) ← AMOUNT (+15%)
- Location: India
- Device: iPhone
Risk: 10 + 15 = 25 → APPROVE (NOT OTP, too low)
```

### ✅ Example 5: Location + Amount (PERFECT FOR OTP)
```
Baseline:
- Amount: $100
- Location: Mumbai, India
- Device: iPhone
- IP: 192.168.1.1

Current:
- Amount: $200 (2x) ← AMOUNT (+25%)
- Location: USA ← LOCATION (+50%)
- Device: iPhone
- IP: 192.168.1.1 (VPN/same ISP)
Risk: 10 + 25 + 50 = 85 → FREEZE (too high)

Modified scenario (better):
- Amount: $120 (1.2x) ← AMOUNT (+0%, <1.5x)
- Location: USA ← LOCATION (+50%)
- Device: iPhone
- IP: same
Risk: 10 + 0 + 50 = 60 → REQUIRE_OTP ✓
```

## OTP Threshold Math

| Combination | Risk | Action |
|-------------|------|--------|
| Location only (50%) | 60 | ✅ OTP |
| Device only (40%) | 50 | ✅ OTP |
| IP only (35%) | 45 | ❌ FLAG |
| Merchant only (30%) | 40 | ❌ FLAG |
| Amount 1.5x (15%) + Device | 65 | ⏸️ HOLD |
| Amount 1.5x + Merchant | 55 | ✅ OTP |
| Amount 2x (25%) + Merchant | 65 | ⏸️ HOLD |
| Amount 2x + Category | 55 | ✅ OTP |
| Rapid (40%) + Merchant | 80 | ❄️ FREEZE |
| Rapid + Device | 90 | 🛑 BLOCK |
| All 4 params (50+40+35+25) | 100 | 🛑 BLOCK |

## OTP Implementation Details

**When OTP is Sent:**
```json
{
  "action": "REQUIRE_OTP",
  "risk_level": "HIGH",
  "final_risk_score": 55,
  "alert_message": "OTP verification required. Risk score 55/100.",
  "secondary_actions": ["SEND_OTP_TO_CUSTOMER"]
}
```

**Customer Flow:**
1. Customer attempts transaction
2. SafeNest flags it as HIGH risk (50-64)
3. OTP sent to registered phone
4. Customer enters OTP
5. Transaction proceeds if OTP valid
6. If no OTP within 5 mins → Transaction auto-declined

**Parameters Tracked in OTP Decision:**
- ✓ Location country
- ✓ Device ID
- ✓ IP address
- ✓ Transaction amount (ratio to baseline)
- ✓ Time gap since last transaction
- ✓ Merchant name
- ✓ Merchant category

## Quick Reference

**ALWAYS OTP (Score 50-64):**
- Location changed (baseline 50)
- Device changed (baseline 40)
- 2 moderate changes combined

**NEVER OTP (Score <50):**
- Single small change (<30%)
- Amount slightly higher (<15%)
- No changes (score 10)

**NEVER OTP (Score ≥65):**
- Multiple changes compound to >65
- Triggers HOLD, FREEZE, or BLOCK instead
