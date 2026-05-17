"""SafeNest v2.0 — Response Agent: Action Engine + Blockchain"""

import time, uuid, hashlib
from datetime import datetime
from typing import List, Tuple

THRESHOLDS = {"block":90, "freeze":70, "otp":50, "flag":30}

class ResponseAgent:
    def __init__(self, db):
        self.db = db

    async def respond(self, tx, sentry: dict, auditor: dict) -> dict:
        start = time.time()

        # Combine scores: 60% sentry + 40% auditor
        auditor_score  = self._auditor_score(auditor)
        final_score    = min(100, int(sentry["risk_score"] * 0.6 + auditor_score * 0.4))

        # Hard overrides
        if auditor["kyc_status"] == "FAILED":      final_score = max(final_score, 95)
        if auditor["sar_required"]:                 final_score = max(final_score, 75)

        action, risk_level = self._decide(final_score)
        secondary          = self._secondary(action, auditor)
        alert_msg          = self._alert(action, final_score, auditor)
        reasoning          = self._reasoning(final_score, sentry, auditor, action)
        block_hash         = self._write_block(tx.transaction_id or "UNKNOWN", action, final_score)

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

    def _auditor_score(self, auditor: dict) -> int:
        base = 0
        if auditor["compliance_status"] == "NON_COMPLIANT": base = 85
        elif auditor["compliance_status"] == "FLAGGED":     base = 45
        base += min(30, len(auditor["regulatory_flags"]) * 8)
        if auditor["kyc_status"]       == "FAILED":       base = max(base, 90)
        if auditor["watchlist_status"] == "MATCH_FOUND":  base = max(base, 70)
        if auditor["sar_required"]:                        base = max(base, 75)
        if auditor["ctr_required"]:                        base += 10
        return min(100, base)

    def _decide(self, score: int) -> Tuple[str, str]:
        if score >= THRESHOLDS["block"]:  return "BLOCK",          "CRITICAL"
        if score >= THRESHOLDS["freeze"]: return "FREEZE_ACCOUNT", "CRITICAL"
        if score >= THRESHOLDS["otp"]:    return "REQUIRE_OTP",    "HIGH"
        if score >= THRESHOLDS["flag"]:   return "FLAG_FOR_REVIEW", "MEDIUM"
        return "APPROVE", "LOW"

    def _secondary(self, action: str, auditor: dict) -> List[str]:
        s = []
        if action in ("BLOCK","FREEZE_ACCOUNT"):
            s += ["NOTIFY_SECURITY_TEAM","SEND_SMS_ALERT_TO_CUSTOMER"]
        if auditor["sar_required"]: s.append("FILE_SAR_REPORT")
        if auditor["ctr_required"]: s.append("FILE_CTR_REPORT")
        if action == "BLOCK":       s.append("ESCALATE_TO_COMPLIANCE_OFFICER")
        return s

    def _alert(self, action, score, auditor) -> str:
        msgs = {
            "APPROVE":          f"Transaction approved. Risk score {score}/100. No significant threats.",
            "FLAG_FOR_REVIEW":  f"Flagged for review. Risk score {score}/100. Analyst attention required.",
            "REQUIRE_OTP":      f"OTP verification required. Risk score {score}/100. Transaction held.",
            "REQUIRE_BIOMETRIC":f"Biometric verification required. Risk score {score}/100.",
            "FREEZE_ACCOUNT":   f"CRITICAL: Account frozen. Risk score {score}/100. SAR: {auditor['sar_required']}.",
            "BLOCK":            f"CRITICAL: Transaction blocked. Risk score {score}/100. Authorities may be notified.",
        }
        return msgs.get(action, f"Action: {action}. Score: {score}/100.")

    def _reasoning(self, score, sentry, auditor, action) -> str:
        parts = []
        if sentry["fraud_indicators"]:
            parts.append(f"Fraud: {'; '.join(sentry['fraud_indicators'][:2])}")
        if auditor["regulatory_flags"]:
            parts.append(f"Compliance: {'; '.join(auditor['regulatory_flags'][:2])}")
        if not parts:
            parts.append("No significant risk indicators")
        return f"Score {score}/100. Action: {action}. {'. '.join(parts)}."

    def _write_block(self, tx_id: str, action: str, risk_score: int) -> str:
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
