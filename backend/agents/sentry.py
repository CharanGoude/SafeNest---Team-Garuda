"""SafeNest v2.0 — Sentry Agent: Fraud Detection"""

import os, json, time, asyncio
from typing import List, Tuple

try:
    import google.generativeai as genai
    GEMINI_OK = True
except ImportError:
    GEMINI_OK = False

HIGH_RISK_MERCHANTS   = {"CryptoFast","QuickCash247","AnonPay","DarkMart","FastCoin","CryptoSwap","AnonymousPay","CashFlash"}
SUSPICIOUS_IP_PFXS    = ("185.","91.108.","45.142.","95.174.","194.165.")
HIGH_RISK_COUNTRIES   = {"KP","IR","SY","CU","SD"}

class SentryAgent:
    def __init__(self):
        self.model = None
        api_key = os.getenv("GOOGLE_API_KEY")
        if GEMINI_OK and api_key:
            try:
                genai.configure(api_key=api_key)
                self.model = genai.GenerativeModel(
                    "gemini-1.5-flash",
                    generation_config={"temperature":0.1,"max_output_tokens":512}
                )
            except Exception as e:
                print(f"[Sentry] Gemini init failed: {e}")

    async def analyze(self, tx) -> dict:
        start = time.time()
        rule_score, indicators = self._rules(tx)

        if self.model and rule_score >= 20:
            try:
                ai_score, summary = await self._gemini(tx, rule_score, indicators)
                final = min(100, int(ai_score * 0.6 + rule_score * 0.4))
            except Exception as e:
                print(f"[Sentry] Gemini failed: {e}")
                final, summary = rule_score, self._summary(rule_score, indicators)
        else:
            final, summary = rule_score, self._summary(rule_score, indicators)

        return {
            "risk_score":          final,
            "fraud_indicators":    indicators,
            "behavioural_summary": summary,
            "processing_ms":       int((time.time()-start)*1000)
        }

    def _rules(self, tx) -> Tuple[int, List[str]]:
        score, flags = 0, []

        # Amount vs user average
        if tx.user_avg_transaction > 0:
            ratio = tx.amount / tx.user_avg_transaction
            if ratio > 5.0:
                score += 30; flags.append(f"Amount {ratio:.1f}x above user average (${tx.user_avg_transaction:.0f})")
            elif ratio > 3.0:
                score += 15; flags.append(f"Amount {ratio:.1f}x above user average")

        # High absolute amount
        if tx.amount > 10000:
            score += 15; flags.append(f"High value transaction: ${tx.amount:,.2f}")
        elif tx.amount > 5000:
            score += 8

        # New device
        if tx.is_new_device:
            score += 20; flags.append("Transaction from unrecognized device")

        # Velocity
        if tx.previous_transaction_minutes_ago is not None:
            if tx.previous_transaction_minutes_ago <= 3:
                score += 25; flags.append(f"Rapid transactions: {tx.previous_transaction_minutes_ago} min since last TX")
            elif tx.previous_transaction_minutes_ago <= 10:
                score += 12; flags.append(f"Elevated velocity: {tx.previous_transaction_minutes_ago} min since last TX")

        # Risky merchant
        if tx.merchant_name in HIGH_RISK_MERCHANTS:
            score += 20; flags.append(f"High-risk merchant: {tx.merchant_name}")

        # Risky country
        if tx.location_country.upper() in HIGH_RISK_COUNTRIES:
            score += 25; flags.append(f"High-risk jurisdiction: {tx.location_country}")

        # Suspicious IP
        if any(tx.ip_address.startswith(p) for p in SUSPICIOUS_IP_PFXS):
            score += 15; flags.append(f"Suspicious IP range: {tx.ip_address}")

        # New account + large amount
        if tx.account_age_days < 30 and tx.amount > 1000:
            score += 20; flags.append(f"New account ({tx.account_age_days}d) with large transaction")

        # Crypto/transfer + large amount
        if tx.merchant_category in ("CRYPTO","TRANSFER") and tx.amount > 3000:
            score += 10; flags.append(f"Large {tx.merchant_category} transaction")

        return min(100, score), flags

    async def _gemini(self, tx, rule_score, indicators) -> Tuple[int, str]:
        prompt = f"""You are a senior fraud analyst. Analyze this transaction. Respond ONLY with JSON.

Transaction:
- User: {tx.user_id}, Account age: {tx.account_age_days} days
- Amount: ${tx.amount:,.2f} (avg: ${tx.user_avg_transaction:,.2f})
- Merchant: {tx.merchant_name} ({tx.merchant_category})
- Location: {tx.location_city or 'Unknown'}, {tx.location_country}
- Device: {'NEW/UNKNOWN' if tx.is_new_device else 'Known'}
- IP: {tx.ip_address}
- Minutes since last TX: {tx.previous_transaction_minutes_ago or 'Unknown'}
- Rule engine flags ({rule_score}/100): {', '.join(indicators) if indicators else 'None'}

Return ONLY this JSON:
{{"risk_score": <0-100>, "reasoning": "<2 sentence analysis>"}}"""

        loop = asyncio.get_event_loop()
        resp = await loop.run_in_executor(None, lambda: self.model.generate_content(prompt))
        text = resp.text.strip()
        if "```" in text:
            text = text.split("```")[1]
            if text.startswith("json"): text = text[4:]
        data = json.loads(text.strip())
        return int(data.get("risk_score", rule_score)), data.get("reasoning", "")

    def _summary(self, score, flags):
        if score >= 75: return f"HIGH FRAUD RISK. {len(flags)} critical indicators: {'; '.join(flags[:2])}."
        if score >= 50: return f"ELEVATED RISK. {len(flags)} suspicious patterns: {'; '.join(flags[:2])}."
        if score >= 25: return f"MODERATE RISK. {len(flags)} minor flags. Monitor this transaction."
        return "LOW RISK. Transaction consistent with normal user behaviour."
