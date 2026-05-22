"""
SafeNest v2.0 - Coordinator Agent Test Examples
Demonstrates baseline-comparison transaction scoring
"""

# Example 1: Baseline Transaction (First Transaction)
# Expected: Low risk, auto-approved, baseline saved
baseline_example = {
    "user_id": "user_rahul_k",
    "account_number": "ACC101RAHUL",
    "transaction_id": "TX001",
    "amount": 500.0,
    "location_country": "IN",
    "location_city": "Mumbai",
    "device_id": "iPhone_14_ABC",
    "ip_address": "192.168.1.100",
    "merchant_name": "Amazon India",
    "merchant_category": "RETAIL",
    "is_baseline": True,
    "risk_score": 10,
    "action": "APPROVE",
    "alert": "Transaction approved. Baseline profile established."
}

# Example 2: Transaction with Location Change
# Expected: Risk 60%, OTP required
location_change_example = {
    "user_id": "user_rahul_k",
    "account_number": "ACC101RAHUL",
    "transaction_id": "TX002",
    "amount": 500.0,
    "location_country": "US",  # CHANGED from IN
    "location_city": "New York",
    "device_id": "iPhone_14_ABC",  # Same
    "ip_address": "192.168.1.100",  # Same
    "merchant_name": "Amazon",
    "merchant_category": "RETAIL",
    "is_baseline": False,
    "risk_score": 60,  # 10 base + 50 location
    "action": "REQUIRE_OTP",
    "comparison_indicators": [
        "Country location changed: IN → US (+50%)"
    ],
    "parameter_changes": [
        "Location: IN → US (+50%)"
    ],
    "alert": "OTP verification required. Risk score 60/100."
}

# Example 3: Transaction with Device + IP Change
# Expected: Risk 75%, Account frozen
device_and_ip_change = {
    "user_id": "user_rahul_k",
    "account_number": "ACC101RAHUL",
    "transaction_id": "TX003",
    "amount": 500.0,
    "location_country": "IN",  # Same
    "location_city": "Mumbai",
    "device_id": "Unknown_Device_XYZ",  # CHANGED
    "ip_address": "91.108.50.200",  # CHANGED
    "merchant_name": "Amazon India",
    "merchant_category": "RETAIL",
    "is_baseline": False,
    "risk_score": 85,  # 10 base + 40 device + 35 IP
    "action": "FREEZE_ACCOUNT",
    "comparison_indicators": [
        "Transaction from unrecognized device",
        "New IP address detected"
    ],
    "parameter_changes": [
        "Device: iPhone_14_ABC → Unknown_Device_XYZ (+40%)",
        "IP Address: 192.168.1.100 → 91.108.50.200 (+35%)"
    ],
    "alert": "ALERT: Account frozen due to suspicious activity. Risk score 85/100."
}

# Example 4: Rapid Transaction + Merchant Change
# Expected: Risk 50%, OTP required
rapid_merchant_change = {
    "user_id": "user_rahul_k",
    "account_number": "ACC101RAHUL",
    "transaction_id": "TX004",
    "amount": 500.0,
    "location_country": "IN",
    "location_city": "Mumbai",
    "device_id": "iPhone_14_ABC",
    "ip_address": "192.168.1.100",
    "merchant_name": "Flipkart",  # CHANGED
    "merchant_category": "RETAIL",  # Same
    "previous_transaction_minutes_ago": 2,  # RAPID (< 3 min = +40%)
    "is_baseline": False,
    "risk_score": 50,  # 10 base + 40 rapid
    "action": "REQUIRE_OTP",
    "comparison_indicators": [
        "Rapid transactions: 2 min since last TX (+40%)"
    ],
    "parameter_changes": [
        "Rapid transaction: 2 min since last (+40%)"
    ],
    "alert": "OTP verification required. Risk score 50/100."
}

# Example 5: Amount Increase (2.5x) + Location Change
# Expected: Risk 100 (CAPPED), BLOCK
amount_and_location = {
    "user_id": "user_priya_m",
    "account_number": "ACC102PRIYA",
    "transaction_id": "TX005",
    "baseline_amount": 800.0,
    "amount": 2000.0,  # 2.5x = +25%
    "location_country": "US",  # CHANGED from IN = +50%
    "location_city": "Chicago",
    "device_id": "Samsung_S23",
    "ip_address": "192.168.2.50",
    "merchant_name": "Crypto Exchange",
    "merchant_category": "CRYPTO",
    "is_baseline": False,
    "risk_score": 100,  # 10 + 25 + 50 + 35 (IP) = 120 → CAPPED at 100
    "action": "BLOCK",
    "comparison_indicators": [
        "Transaction amount 2.5x baseline: $800 → $2000",
        "Country location changed: IN → US",
        "New IP address detected",
        "Multiple suspicious changes detected (3 parameters)"
    ],
    "parameter_changes": [
        "Amount: $800 → $2000 (ratio: 2.5x, +25%)",
        "Location: IN → US (+50%)",
        "IP Address: 192.168.2.50 → new (+35%)"
    ],
    "alert": "CRITICAL: Transaction blocked. Risk score 100/100. Contact support."
}

# Example 6: Safe Repeat Transaction (All Same)
# Expected: Risk 10%, APPROVE
safe_repeat = {
    "user_id": "user_carlos_r",
    "account_number": "ACC103CARLOS",
    "transaction_id": "TX006",
    "amount": 1200.0,  # Same as baseline
    "location_country": "US",  # Same
    "location_city": "New York",  # Same
    "device_id": "MacBook_Pro",  # Same
    "ip_address": "74.52.100.50",  # Same
    "merchant_name": "Netflix",  # Same
    "merchant_category": "STREAMING",  # Same
    "previous_transaction_minutes_ago": 3600,  # 1 hour, not rapid
    "is_baseline": False,
    "risk_score": 10,  # Base only
    "action": "APPROVE",
    "comparison_indicators": [
        "All parameters match baseline"
    ],
    "parameter_changes": [],
    "alert": "Transaction approved. Risk score 10/100."
}

# Example 7: Hold Transaction (65-74 range)
# Expected: Risk 70%, HOLD
hold_transaction = {
    "user_id": "user_anna_s",
    "account_number": "ACC104ANNA",
    "transaction_id": "TX007",
    "baseline_amount": 600.0,
    "amount": 1200.0,  # 2x = +25%
    "location_country": "GB",  # Same
    "location_city": "London",
    "device_id": "Samsung_Phone",  # CHANGED from Pixel_7 = +40%
    "ip_address": "82.50.100.1",  # Same
    "merchant_name": "Harrods",  # CHANGED
    "merchant_category": "RETAIL",
    "previous_transaction_minutes_ago": 120,  # 2 hours, not rapid
    "is_baseline": False,
    "risk_score": 70,  # 10 + 25 (amount) + 40 (device) - but let's cap at contribution
    "action": "HOLD_TRANSACTION",
    "comparison_indicators": [
        "Transaction amount 2x baseline",
        "New device detected",
        "Different merchant"
    ],
    "parameter_changes": [
        "Amount: $600 → $1200 (ratio: 2x, +25%)",
        "Device: Pixel_7 → Samsung_Phone (+40%)"
    ],
    "alert": "Transaction held for verification. Risk score 70/100."
}

# Summary of Risk Score Ranges and Actions
RISK_SCORE_SUMMARY = """
SafeNest Coordinator Agent - Risk Score Decision Matrix

Score Range    | Action           | Risk Level | Description
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
0-9            | APPROVE          | LOW        | Baseline transactions
10-29          | APPROVE          | LOW        | Safe transaction, no changes
30-49          | FLAG_FOR_REVIEW  | MEDIUM     | Analyst review required
50-64          | REQUIRE_OTP      | HIGH       | OTP verification needed
65-74          | HOLD_TRANSACTION | HIGH       | Transaction held for review
75-89          | FREEZE_ACCOUNT   | CRITICAL   | Account frozen, alerts sent
90-100         | BLOCK            | CRITICAL   | Transaction rejected

Parameter Risk Contributions:
  Location Country Change      → +50%
  Device ID Change             → +40%
  IP Address Change            → +35%
  Amount 2x-3x Baseline        → +25%
  Amount 3x-5x Baseline        → +35%
  Amount 5x+ Baseline          → +50%
  Rapid Transaction (<3 min)   → +40%
  Rapid Transaction (<10 min)  → +25%
  Rapid Transaction (<30 min)  → +15%
  Merchant Name Change         → +30%
  Merchant Category Change     → +20%
  Multiple Parameters (>2)     → +10% per extra

Base Risk Score: 10%
Maximum: 100% (capped)
"""

print(RISK_SCORE_SUMMARY)

# Test Cases for OTP Trigger (50-64 range)
OTP_TEST_CASES = """
✅ OTP Trigger Test Cases (Score 50-64)

1. Location Change Only:
   Base: 10 + Location: 50 = 60 ✓

2. Device Change Only:
   Base: 10 + Device: 40 = 50 ✓

3. Amount 2x + Merchant:
   Base: 10 + Amount: 25 + Merchant: 20 = 55 ✓

4. Amount 1.5x + Device:
   Base: 10 + Amount: 15 + Device: 40 = 65 ✓ (Upper bound)

5. Rapid (<10min) + Amount 1.5x:
   Base: 10 + Rapid: 25 + Amount: 15 = 50 ✓ (Lower bound)

❌ Below OTP Range (<50):
- Single small change: 10 + 15 = 25
- Amount increase: 10 + 15 = 25
- Rapid transaction: 10 + 15 = 25

❌ Above OTP Range (>64):
- Location + Device: 10 + 50 + 40 = 100 (→ CAPPED, BLOCK)
- Location + IP: 10 + 50 + 35 = 95 (→ BLOCK)
- Device + IP: 10 + 40 + 35 = 85 (→ FREEZE)
- Amount 2x + Device: 10 + 25 + 40 = 75 (→ FREEZE)
"""

print(OTP_TEST_CASES)
