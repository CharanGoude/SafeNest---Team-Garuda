"""SafeNest v2.0 — Response Agent: Action Engine + Blockchain"""

import time, uuid, hashlib
from datetime import datetime
from typing import List, Tuple

# Updated thresholds for Coordinator-based scoring
THRESHOLDS = {
    "block":   90,      # 90+ = Block transaction
    "freeze":  75,      # 75-89 = Freeze account
    "hold":    65,      # 65-74 = Hold for verification
    "otp":     50,      # 50-64 = Require OTP
    "flag":    30,      # 30-49 = Flag for review
}

class ResponseAgent:
    def __init__(self, db):
        self.db = db

    async def respond(self, tx, coordinator: dict) -> dict:
        """
        Respond based on Coordinator's baseline comparison risk score.
        No more Sentry/Auditor combination - pure comparison-based logic.
        """
        start = time.time()

        final_score = coordinator["risk_score"]
        is_baseline = coordinator.get("is_baseline", False)

        # If baseline transaction, always approve
        if is_baseline:
            action = "APPROVE"
            risk_level = "LOW"
            reasoning = "Baseline transaction approved. Establishing user profile."
        else:
            action, risk_level = self._decide(final_score)
            reasoning = self._reasoning(final_score, coordinator)

        secondary = self._secondary(action)
        alert_msg = self._alert(action, final_score, is_baseline)
        block_hash = self._write_block(tx.transaction_id or "UNKNOWN", action, final_score)

        return {
            "action":            action,
            "risk_level":        risk_level,
            "final_risk_score":  final_score,
            "reasoning":         reasoning,
            "alert_message":     alert_msg,
            "secondary_actions": secondary,
            "processing_ms":     int((time.time()-start)*1000),
            "blockchain_hash":   block_hash
        }

    def _decide(self, score: int) -> Tuple[str, str]:
        """Decide action based on coordinator risk score."""
        if score >= THRESHOLDS["block"]:      return "BLOCK",          "CRITICAL"
        if score >= THRESHOLDS["freeze"]:     return "FREEZE_ACCOUNT", "CRITICAL"
        if score >= THRESHOLDS["hold"]:       return "HOLD_TRANSACTION", "HIGH"
        if score >= THRESHOLDS["otp"]:        return "REQUIRE_OTP",    "HIGH"
        if score >= THRESHOLDS["flag"]:       return "FLAG_FOR_REVIEW", "MEDIUM"
        return "APPROVE", "LOW"

    def _secondary(self, action: str) -> List[str]:
        """Determine secondary actions."""
        s = []
        if action == "BLOCK":
            s += ["NOTIFY_SECURITY_TEAM", "SEND_SMS_ALERT_TO_CUSTOMER", "ESCALATE_TO_COMPLIANCE_OFFICER"]
        elif action == "FREEZE_ACCOUNT":
            s += ["NOTIFY_SECURITY_TEAM", "SEND_SMS_ALERT_TO_CUSTOMER"]
        elif action == "REQUIRE_OTP":
            s.append("SEND_OTP_TO_CUSTOMER")
        elif action == "FLAG_FOR_REVIEW":
            s.append("QUEUE_FOR_ANALYST_REVIEW")
        return s

    def _alert(self, action, score, is_baseline) -> str:
        """Generate user-facing alert message."""
        if is_baseline:
            return "Transaction approved. Baseline profile established."
        
        msgs = {
            "APPROVE":          f"Transaction approved. Risk score {score}/100.",
            "FLAG_FOR_REVIEW":  f"Transaction flagged for review. Risk score {score}/100.",
            "REQUIRE_OTP":      f"OTP verification required. Risk score {score}/100.",
            "HOLD_TRANSACTION": f"Transaction held for verification. Risk score {score}/100.",
            "FREEZE_ACCOUNT":   f"ALERT: Account frozen due to suspicious activity. Risk score {score}/100.",
            "BLOCK":            f"CRITICAL: Transaction blocked. Risk score {score}/100. Contact support.",
        }
        return msgs.get(action, f"Action: {action}. Score: {score}/100.")

    def _reasoning(self, score, coordinator) -> str:
        """Build reasoning summary."""
        indicators = coordinator.get("comparison_indicators", [])
        param_changes = coordinator.get("parameter_changes", [])
        
        if not indicators:
            return f"Score {score}/100. No significant deviations from baseline."
        
        main_indicator = indicators[0] if indicators else "Profile deviation detected"
        param_summary = "; ".join(param_changes[:2]) if param_changes else ""
        
        if param_summary:
            return f"Score {score}/100. Changes: {param_summary}."
        return f"Score {score}/100. {main_indicator}"

    def _write_block(self, tx_id: str, action: str, risk_score: int) -> str:
        """Write transaction to blockchain ledger."""
        prev_hash  = self.db.get_last_block_hash()
        block_id   = str(uuid.uuid4())[:8].upper()
        timestamp  = datetime.utcnow().isoformat()
        content    = f"{block_id}{tx_id}{action}{risk_score}{timestamp}{prev_hash}"
        block_hash = hashlib.sha256(content.encode()).hexdigest()
        self.db.save_block({
            "block_id":       block_id,
            "transaction_id": tx_id,
            "action":         action,
            "risk_score":     risk_score,
            "block_hash":     block_hash,
            "prev_hash":      prev_hash,
            "timestamp":      timestamp,
        })
        return block_hash
