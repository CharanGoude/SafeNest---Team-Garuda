"""SafeNest v2.0 — Auditor Agent: KYC / AML / Compliance"""

import os, json, time, asyncio
from typing import List, Tuple

try:
    import google.generativeai as genai
    GEMINI_OK = True
except ImportError:
    GEMINI_OK = False

KYC_BLACKLIST        = {"ACC999BLACKLIST","ACC666FRAUD","ACC000SANCTIONED","ACC888BLOCKED","ACC111FROZEN"}
AML_HIGH_RISK        = {"KP","IR","SY","CU","SD","MM","YE","SO","LY"}
MERCHANT_WATCHLIST   = {"CryptoFast","QuickCash247","AnonPay","DarkMart","FastCoin","CryptoSwap","AnonymousPay","CashFlash"}
CTR_THRESHOLD        = 10_000.0
STRUCTURING_LOW      = 8_000.0
STRUCTURING_HIGH     = 9_999.99

class AuditorAgent:
    def __init__(self):
        self.model = None
        api_key = os.getenv("GOOGLE_API_KEY")
        if GEMINI_OK and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(
                    "gemini-1.5-flash",
                    generation_config={"temperature":0.0,"max_output_tokens":256}
                )
            except Exception as e:
                print(f"[Auditor] Gemini init failed: {e}")

    async def verify(self, tx, sentry_score: int) -> dict:
        start = time.time()
        kyc, aml, watchlist, flags, ctr, sar = self._rules(tx, sentry_score)

        if kyc == "FAILED" or watchlist == "MATCH_FOUND":
            compliance = "NON_COMPLIANT"
        elif aml == "FLAGGED" or flags:
            compliance = "FLAGGED"
        else:
            compliance = "COMPLIANT"

        if self.model and compliance != "COMPLIANT":
            try:
                ai_flags = await self._gemini(tx, kyc, aml, watchlist)
                flags = list(set(flags + ai_flags))
            except Exception as e:
                print(f"[Auditor] Gemini failed: {e}")

        return {
            "compliance_status": compliance,
            "kyc_status":        kyc,
            "aml_status":        aml,
            "watchlist_status":  watchlist,
            "ctr_required":      ctr,
            "sar_required":      sar,
            "regulatory_flags":  flags,
            "processing_ms":     int((time.time()-start)*1000)
        }

    def _rules(self, tx, sentry_score) -> Tuple[str,str,str,List[str],bool,bool]:
        flags = []

        # KYC
        if tx.account_number in KYC_BLACKLIST:
            kyc = "FAILED"
            flags.append(f"CRITICAL: Account {tx.account_number} on KYC blacklist")
        else:
            kyc = "VERIFIED"

        # AML
        aml_flags = []
        if tx.location_country.upper() in AML_HIGH_RISK:
            aml_flags.append(f"Transaction from high-risk jurisdiction: {tx.location_country}")
        if STRUCTURING_LOW <= tx.amount <= STRUCTURING_HIGH:
            aml_flags.append(f"Potential structuring: ${tx.amount:,.2f} just below CTR threshold")
        if tx.previous_transaction_minutes_ago is not None and tx.previous_transaction_minutes_ago < 5 and tx.amount > 2000:
            aml_flags.append("Rapid high-value transfer sequence — possible layering")
        if tx.merchant_category == "CRYPTO" and tx.amount > 5000:
            aml_flags.append("Large cryptocurrency transaction — AML monitoring required")
        aml = "FLAGGED" if aml_flags else "CLEAR"
        flags.extend(aml_flags)

        # Watchlist
        if tx.merchant_name in MERCHANT_WATCHLIST:
            watchlist = "MATCH_FOUND"
            flags.append(f"Merchant '{tx.merchant_name}' on financial crime watchlist")
        else:
            watchlist = "CLEAR"

        # CTR
        ctr = tx.amount >= CTR_THRESHOLD
        if ctr:
            flags.append(f"CTR required: ${tx.amount:,.2f} exceeds $10,000")

        # SAR
        sar = kyc == "FAILED" or watchlist == "MATCH_FOUND" or (sentry_score >= 70 and aml == "FLAGGED")
        if sar:
            flags.append("SAR filing required: multiple high-risk indicators")

        return kyc, aml, watchlist, flags, ctr, sar

    async def _gemini(self, tx, kyc, aml, watchlist) -> List[str]:
        prompt = f"""You are a bank compliance officer. Review for additional regulatory concerns.

Transaction:
- Account: {tx.account_number} (KYC: {kyc})
- Amount: ${tx.amount:,.2f} | Type: {tx.transaction_type}
- Merchant: {tx.merchant_name} ({tx.merchant_category}) | Watchlist: {watchlist}
- Country: {tx.location_country} | AML: {aml}
- Account age: {tx.account_age_days} days

Return ONLY JSON (no markdown):
{{"additional_flags": ["<flag1>", "<flag2>"]}}

Return empty array if no additional concerns."""

        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, lambda: self.model.generate_content(prompt))
        text = resp.text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
        return json.loads(text.strip()).get("additional_flags", [])
