"""
Auditor Agent — Regulatory Compliance Verification
Performs KYC, AML, Watchlist screening using Google Gemini.
"""
import os
import json
import google.generativeai as genai
from models import Transaction


class AuditorAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None
        self.name = "Auditor Agent"

        # Simulated watchlist
        self.watchlist_accounts = {"ACC999BLACKLIST", "ACC888SANCTION", "BLOCKEDUSER01"}
        self.high_risk_merchants = {"CRYPTO_UNREGULATED", "DARKWEB_MARKET", "ANONYMOUS_TRANSFER"}

    def _build_prompt(self, tx: Transaction, sentry_result: dict) -> str:
        return f"""You are the Auditor Agent in SafeNest, responsible for regulatory compliance verification.

Perform KYC, AML, and compliance checks on this transaction.

TRANSACTION:
- ID: {tx.transaction_id}
- User: {tx.user_id}
- Account: {tx.account_number}
- Amount: {tx.amount} {tx.currency}
- Type: {tx.transaction_type}
- Country: {tx.location_country}
- Merchant: {tx.merchant_name or 'N/A'} ({tx.merchant_category or 'N/A'})
- Account Age: {tx.account_age_days or 'N/A'} days

SENTRY FRAUD SCORE: {sentry_result.get('fraud_risk_score', 0)}/100

COMPLIANCE CHECKS REQUIRED:
1. KYC Verification — Is the user identity verifiable? Red flags?
2. AML Monitoring — Does this show money laundering patterns (structuring, layering, rapid movement)?
3. Watchlist Screening — Flag if account matches known bad actors
4. Transaction Pattern — Is this consistent with legitimate business?
5. Regulatory Threshold — Transactions above $10,000 require reporting (CTR)

Respond ONLY in valid JSON:
{{
  "kyc_status": "<VERIFIED|FLAGGED|FAILED>",
  "aml_status": "<CLEAR|SUSPICIOUS|VIOLATION>",
  "watchlist_status": "<CLEAR|MATCH_FOUND>",
  "ctr_required": <true|false>,
  "compliance_status": "<COMPLIANT|REVIEW_REQUIRED|NON_COMPLIANT>",
  "compliance_notes": "<2-3 sentence summary>",
  "regulatory_flags": ["<flag1>", "<flag2>"]
}}"""

    async def verify(self, tx: Transaction, sentry_result: dict) -> dict:
        # First do deterministic checks
        deterministic = self._deterministic_checks(tx)

        if not self.model:
            return {**deterministic, "agent": self.name}

        try:
            response = self.model.generate_content(self._build_prompt(tx, sentry_result))
            text = response.text.strip()
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            ai_result = json.loads(text)

            # Merge: deterministic overrides on hard violations
            if deterministic.get("watchlist_hit"):
                ai_result["watchlist_status"] = "MATCH_FOUND"
                ai_result["compliance_status"] = "NON_COMPLIANT"
            if tx.amount >= 10000:
                ai_result["ctr_required"] = True

            ai_result["agent"] = self.name
            return ai_result
        except Exception:
            return {**deterministic, "agent": self.name}

    def _deterministic_checks(self, tx: Transaction) -> dict:
        watchlist_hit = tx.account_number in self.watchlist_accounts or tx.user_id in self.watchlist_accounts
        merchant_risk = tx.merchant_name in self.high_risk_merchants if tx.merchant_name else False
        ctr_required = tx.amount >= 10000
        aml_flags = []

        # Structuring check (just below reporting threshold)
        if 9000 <= tx.amount < 10000:
            aml_flags.append("Potential structuring — amount just below CTR threshold")

        if merchant_risk:
            aml_flags.append(f"High-risk merchant category: {tx.merchant_name}")

        compliance = "NON_COMPLIANT" if watchlist_hit else "REVIEW_REQUIRED" if aml_flags else "COMPLIANT"

        return {
            "kyc_status": "FAILED" if watchlist_hit else "VERIFIED",
            "aml_status": "VIOLATION" if watchlist_hit else "SUSPICIOUS" if aml_flags else "CLEAR",
            "watchlist_status": "MATCH_FOUND" if watchlist_hit else "CLEAR",
            "ctr_required": ctr_required,
            "compliance_status": compliance,
            "compliance_notes": f"{'Watchlist match detected. Account flagged.' if watchlist_hit else 'No watchlist match.'} {'CTR filing required.' if ctr_required else ''} {len(aml_flags)} AML flag(s).",
            "regulatory_flags": aml_flags,
            "watchlist_hit": watchlist_hit
        }
