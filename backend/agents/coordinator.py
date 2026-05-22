"""SafeNest v2.0 — Coordinator Agent: Baseline Transaction Comparison & Risk Scoring"""

import time
from typing import List, Tuple, Optional, Dict


class CoordinatorAgent:
    """
    Compares current transaction to baseline (first transaction).
    Each parameter deviation increases risk score based on severity.
    """

    # Risk percentage increase per parameter change
    RISK_WEIGHTS = {
        "location_change":       50,    # Location mismatch = 50% risk
        "device_change":         40,    # New device = 40% risk
        "ip_change":             35,    # New IP = 35% risk
        "amount_increase":       {      # Amount deviation from baseline
            1.5:  15,               # 50% above = 15%
            2.0:  25,               # 100% above = 25%
            3.0:  35,               # 200% above = 35%
            5.0:  50,               # 400% above = 50%
        },
        "rapid_transaction":     {      # Minutes since last transaction
            3:    40,               # Within 3 min = 40%
            10:   25,               # Within 10 min = 25%
            30:   15,               # Within 30 min = 15%
        },
        "merchant_change":       30,    # Different merchant = 30%
        "merchant_category_change": 20,  # Different category = 20%
        "multiple_parameters":   10,    # Each additional parameter = +10%
    }

    def __init__(self, db):
        self.db = db

    async def analyze(self, tx, baseline_tx: Optional[object] = None) -> dict:
        """
        Analyze transaction compared to baseline.
        If no baseline exists, this becomes the baseline.
        """
        start = time.time()

        # Check if this is the first transaction for this user
        if not baseline_tx:
            baseline_tx = self.db.get_baseline_transaction(tx.user_id, tx.account_number)

        if not baseline_tx:
            # First transaction - approve with low risk
            self.db.save_baseline_transaction({
                "user_id": tx.user_id,
                "account_number": tx.account_number,
                "amount": tx.amount,
                "location_country": tx.location_country,
                "location_city": tx.location_city,
                "merchant_name": tx.merchant_name,
                "merchant_category": tx.merchant_category,
                "device_id": tx.device_id,
                "ip_address": tx.ip_address,
                "timestamp": time.time(),
            })
            return {
                "risk_score": 10,  # Low baseline risk
                "is_baseline": True,
                "comparison_indicators": ["BASELINE_TRANSACTION: First transaction, minimal checks applied"],
                "parameter_changes": [],
                "processing_ms": int((time.time() - start) * 1000)
            }

        # Subsequent transaction - compare to baseline
        risk_score, indicators, param_changes = self._compare_to_baseline(tx, baseline_tx)

        return {
            "risk_score": risk_score,
            "is_baseline": False,
            "comparison_indicators": indicators,
            "parameter_changes": param_changes,
            "processing_ms": int((time.time() - start) * 1000)
        }

    def _compare_to_baseline(self, tx, baseline) -> Tuple[int, List[str], List[str]]:
        """
        Compare all parameters to baseline and calculate risk increase.
        Returns: (risk_score, indicators, parameter_changes)
        """
        risk_score = 10  # Start with base risk
        indicators = []
        param_changes = []
        changes_count = 0

        # 1. LOCATION CHANGE
        if tx.location_country.upper() != baseline.get("location_country", "").upper():
            change_pct = self.RISK_WEIGHTS["location_change"]
            risk_score += change_pct
            param_changes.append(f"Location: {baseline.get('location_country', 'Unknown')} → {tx.location_country} (+{change_pct}%)")
            indicators.append(f"Country location changed: {baseline.get('location_country')} → {tx.location_country}")
            changes_count += 1

        # 2. DEVICE CHANGE
        if tx.device_id != baseline.get("device_id", ""):
            change_pct = self.RISK_WEIGHTS["device_change"]
            risk_score += change_pct
            param_changes.append(f"Device: {baseline.get('device_id', 'Unknown')} → {tx.device_id} (+{change_pct}%)")
            indicators.append(f"New device detected: {tx.device_id}")
            changes_count += 1

        # 3. IP ADDRESS CHANGE
        if tx.ip_address != baseline.get("ip_address", ""):
            change_pct = self.RISK_WEIGHTS["ip_change"]
            risk_score += change_pct
            param_changes.append(f"IP Address: {baseline.get('ip_address', 'Unknown')} → {tx.ip_address} (+{change_pct}%)")
            indicators.append(f"New IP address: {tx.ip_address}")
            changes_count += 1

        # 4. AMOUNT CHANGE (compared to baseline amount)
        if tx.amount != baseline.get("amount", 0):
            amount_ratio = tx.amount / max(baseline.get("amount", 1), 1)
            amount_increase_pct = self._calculate_amount_risk(amount_ratio)
            if amount_increase_pct > 0:
                risk_score += amount_increase_pct
                param_changes.append(f"Amount: ${baseline.get('amount', 0):.2f} → ${tx.amount:.2f} (ratio: {amount_ratio:.2f}x, +{amount_increase_pct}%)")
                indicators.append(f"Transaction amount {amount_ratio:.2f}x baseline: ${baseline.get('amount', 0):.2f} → ${tx.amount:.2f}")
                changes_count += 1

        # 5. RAPID TRANSACTION (minutes since last)
        if tx.previous_transaction_minutes_ago is not None:
            rapid_pct = self._calculate_velocity_risk(tx.previous_transaction_minutes_ago)
            if rapid_pct > 0:
                risk_score += rapid_pct
                param_changes.append(f"Rapid transaction: {tx.previous_transaction_minutes_ago} min since last (+{rapid_pct}%)")
                indicators.append(f"Rapid transactions: {tx.previous_transaction_minutes_ago} min since last TX")
                changes_count += 1

        # 6. MERCHANT CHANGE
        if tx.merchant_name.lower() != baseline.get("merchant_name", "").lower():
            change_pct = self.RISK_WEIGHTS["merchant_change"]
            risk_score += change_pct
            param_changes.append(f"Merchant: {baseline.get('merchant_name', 'Unknown')} → {tx.merchant_name} (+{change_pct}%)")
            indicators.append(f"Different merchant: {baseline.get('merchant_name')} → {tx.merchant_name}")
            changes_count += 1

        # 7. MERCHANT CATEGORY CHANGE
        if tx.merchant_category.upper() != baseline.get("merchant_category", "").upper():
            change_pct = self.RISK_WEIGHTS["merchant_category_change"]
            risk_score += change_pct
            param_changes.append(f"Category: {baseline.get('merchant_category', 'Unknown')} → {tx.merchant_category} (+{change_pct}%)")
            indicators.append(f"Category change: {baseline.get('merchant_category')} → {tx.merchant_category}")
            changes_count += 1

        # 8. MULTIPLE PARAMETER PENALTY
        if changes_count > 2:
            multi_penalty = (changes_count - 2) * self.RISK_WEIGHTS["multiple_parameters"]
            risk_score += multi_penalty
            param_changes.append(f"Multiple parameters changed: +{multi_penalty}% penalty")
            indicators.append(f"Multiple suspicious changes detected ({changes_count} parameters)")

        # Cap risk score at 100
        risk_score = min(100, risk_score)

        return risk_score, indicators, param_changes

    def _calculate_amount_risk(self, ratio: float) -> int:
        """Calculate risk percentage based on amount ratio to baseline."""
        if ratio < 1.5:
            return 0  # No increase for small differences
        elif ratio < 2.0:
            return self.RISK_WEIGHTS["amount_increase"][1.5]
        elif ratio < 3.0:
            return self.RISK_WEIGHTS["amount_increase"][2.0]
        elif ratio < 5.0:
            return self.RISK_WEIGHTS["amount_increase"][3.0]
        else:
            return self.RISK_WEIGHTS["amount_increase"][5.0]

    def _calculate_velocity_risk(self, minutes_ago: int) -> int:
        """Calculate risk percentage based on transaction velocity."""
        if minutes_ago <= 3:
            return self.RISK_WEIGHTS["rapid_transaction"][3]
        elif minutes_ago <= 10:
            return self.RISK_WEIGHTS["rapid_transaction"][10]
        elif minutes_ago <= 30:
            return self.RISK_WEIGHTS["rapid_transaction"][30]
        return 0  # No velocity risk for normal spacing
