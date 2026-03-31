"""
Response Agent — Automated Fraud Mitigation & Security Actions
Decides and executes the appropriate response based on Sentry + Auditor findings.
"""
import os
import json
import google.generativeai as genai
from datetime import datetime
from models import Transaction


class ResponseAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None
        self.name = "Response Agent"

    def _build_prompt(self, tx: Transaction, sentry: dict, auditor: dict) -> str:
        return f"""You are the Response Agent in SafeNest. Your job is to decide the AUTOMATED SECURITY ACTION.

TRANSACTION: {tx.transaction_id} | Amount: ${tx.amount} {tx.currency}
SENTRY RESULT: Risk Score {sentry.get('fraud_risk_score')}/100 | Level: {sentry.get('risk_level')} | Recommendation: {sentry.get('recommendation')}
AUDITOR RESULT: KYC: {auditor.get('kyc_status')} | AML: {auditor.get('aml_status')} | Compliance: {auditor.get('compliance_status')}

AVAILABLE ACTIONS:
- APPROVE: Transaction is safe, process normally
- FLAG_FOR_REVIEW: Suspicious but not definitive — assign to analyst
- REQUIRE_OTP: Force one-time password verification before processing
- REQUIRE_BIOMETRIC: Require facial/biometric verification
- FREEZE_ACCOUNT: Temporarily freeze the account
- BLOCK: Block this transaction immediately
- REPORT_REGULATORY: File a regulatory report (SAR/CTR)
- NOTIFY_ADMIN: Alert security admin team

Respond ONLY in valid JSON:
{{
  "action_taken": "<PRIMARY_ACTION>",
  "secondary_actions": ["<action1>", "<action2>"],
  "reasoning": "<2-3 sentence explanation of why this action was chosen>",
  "alert_message": "<Short user-facing or admin alert message>",
  "severity": "<INFO|WARNING|CRITICAL>",
  "estimated_prevention_value": <estimated dollar amount protected>
}}"""

    async def respond(self, tx: Transaction, sentry: dict, auditor: dict) -> dict:
        # Deterministic hard rules first
        if auditor.get("watchlist_status") == "MATCH_FOUND" or auditor.get("kyc_status") == "FAILED":
            return self._hard_block(tx, "Watchlist match or KYC failure")

        if sentry.get("fraud_risk_score", 0) >= 90:
            return self._hard_block(tx, "Critical fraud risk score")

        if not self.model:
            return self._rule_based_response(tx, sentry, auditor)

        try:
            response = self.model.generate_content(self._build_prompt(tx, sentry, auditor))
            text = response.text.strip()
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            result = json.loads(text)
            result["agent"] = self.name
            result["timestamp"] = datetime.utcnow().isoformat()
            return result
        except Exception:
            return self._rule_based_response(tx, sentry, auditor)

    def _hard_block(self, tx: Transaction, reason: str) -> dict:
        return {
            "agent": self.name,
            "action_taken": "BLOCK",
            "secondary_actions": ["FREEZE_ACCOUNT", "NOTIFY_ADMIN", "REPORT_REGULATORY"],
            "reasoning": f"Hard block triggered: {reason}. Immediate action taken to protect account.",
            "alert_message": f"ALERT: Transaction {tx.transaction_id} BLOCKED. Security team notified.",
            "severity": "CRITICAL",
            "estimated_prevention_value": tx.amount,
            "timestamp": datetime.utcnow().isoformat()
        }

    def _rule_based_response(self, tx: Transaction, sentry: dict, auditor: dict) -> dict:
        score = sentry.get("fraud_risk_score", 0)
        compliance = auditor.get("compliance_status", "COMPLIANT")

        if score >= 70 or compliance == "NON_COMPLIANT":
            action = "BLOCK"
            secondary = ["NOTIFY_ADMIN", "REPORT_REGULATORY"]
            severity = "CRITICAL"
        elif score >= 50 or compliance == "REVIEW_REQUIRED":
            action = "REQUIRE_OTP"
            secondary = ["FLAG_FOR_REVIEW", "NOTIFY_ADMIN"]
            severity = "WARNING"
        elif score >= 30:
            action = "FLAG_FOR_REVIEW"
            secondary = ["REQUIRE_OTP"]
            severity = "WARNING"
        else:
            action = "APPROVE"
            secondary = []
            severity = "INFO"

        return {
            "agent": self.name,
            "action_taken": action,
            "secondary_actions": secondary,
            "reasoning": f"Risk score {score}/100. Compliance: {compliance}. Rule-based action selected.",
            "alert_message": f"Transaction {tx.transaction_id}: {action}",
            "severity": severity,
            "estimated_prevention_value": tx.amount if action == "BLOCK" else 0,
            "timestamp": datetime.utcnow().isoformat()
        }
