# SafeNest v2.0 - Coordinator Agent Implementation Summary

## Overview
Replaced the Auditor Agent with a new **Coordinator Agent** that performs baseline-comparison risk scoring. KYC is now handled by banks directly, so no need for auditor verification.

## Changes Made

### 1. **New Coordinator Agent** (`agents/coordinator.py`)
- Compares all transaction parameters to the **first/baseline transaction**
- Assigns risk percentages for each deviation:
  - **Location Change**: +50%
  - **Device Change**: +40%
  - **IP Address Change**: +35%
  - **Amount Increase** (1.5x): +15% | (2x): +25% | (3x): +35% | (5x+): +50%
  - **Rapid Transactions** (≤3 min): +40% | (≤10 min): +25% | (≤30 min): +15%
  - **Merchant Change**: +30%
  - **Category Change**: +20%
  - **Multiple Parameters** (>2 changes): +10% per extra change

**Key Features:**
- First transaction is baseline with low risk (10%)
- Subsequent transactions compared against baseline
- Baseline automatically saved to database
- Risk score capped at 100

### 2. **Updated Response Agent** (`agents/response.py`)
- New thresholds based on comparison scoring:
  - **90+**: Block transaction (CRITICAL)
  - **75-89**: Freeze account (CRITICAL)
  - **65-74**: Hold transaction (HIGH)
  - **50-64**: Require OTP (HIGH)
  - **30-49**: Flag for review (MEDIUM)
  - **<30**: Approve (LOW)

- Updated secondary actions:
  - Block → Security team notification + customer SMS + compliance escalation
  - Freeze → Security team notification + customer SMS
  - OTP → Send OTP to customer
  - Flag → Queue for analyst review

### 3. **Database Updates** (`agents/db/database.py`)
- **New table**: `baseline_transactions`
  - Stores first transaction for each user/account
  - Fields: user_id, account_number, amount, location, merchant, device, IP, timestamp
  - Unique constraint on (user_id, account_number)

- **New methods**:
  - `save_baseline_transaction()`: Save/update baseline
  - `get_baseline_transaction()`: Retrieve baseline

### 4. **Main Pipeline** (`main.py`)
- **Old**: Sentry + Auditor → Response
- **New**: Coordinator → Response

**New Flow:**
1. Get baseline transaction (if exists)
2. Run Coordinator agent (compares to baseline)
3. Response agent decides action
4. Save transaction and broadcast alerts

- Updated health endpoint: Shows "Coordinator Agent" + "Response Agent"
- Removed Sentry and Auditor dependencies
- Backward compatible: Returns empty Auditor/Sentry results for frontend

## Risk Scoring Example

**Baseline Transaction 1:**
- Amount: $1,000
- Location: IN (India)
- Device: iPhone_14
- IP: 192.168.1.1
- Merchant: Amazon
- Risk Score: 10 (baseline)

**Transaction 2 (Compared to Baseline):**
- Amount: $2,500 (2.5x) → +25%
- Location: US → +50%
- Device: Same → +0%
- IP: 91.108.1.1 (new) → +35%
- Merchant: Different → +30%
- **Risk Score**: 10 + 25 + 50 + 35 + 30 = **150** → capped to **100**
- **Action**: Block (since 100 ≥ 90)

**Transaction 3:**
- Amount: $1,100 (1.1x, <1.5x) → +0%
- Location: IN → +0%
- Device: Same → +0%
- IP: Same → +0%
- Merchant: Amazon → +0%
- **Risk Score**: 10
- **Action**: Approve

## OTP Requirement Rule
When risk score is 50-64:
- **Action**: REQUIRE_OTP
- **Alert**: "OTP verification required. Risk score XX/100."
- **Secondary**: Send OTP to customer

## Testing
Simulate transactions using `/api/v1/simulate?count=5` endpoint. Each scenario now triggers baseline comparison logic.

## Future Enhancements
- Add ML-based anomaly detection
- Integrate with real bank KYC systems
- Add geographic velocity checks
- Implement behavioral profiling
