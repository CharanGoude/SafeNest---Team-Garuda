"""
Sentry Agent — Fraud Pattern Detection & Anomaly Analysis
Uses Google Gemini to analyze transaction behaviour and generate Fraud Risk Score.
"""
import os
import json
import google.generativeai as genai
from models import Transaction


class SentryAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None
        self.name = "Sentry Agent"

    def _build_prompt(self, tx: Transaction) -> str:
        return f"""You are the Sentry Agent in SafeNest, an AI fraud detection system.

Analyze this financial transaction and detect fraud indicators.

TRANSACTION DATA:
- ID: {tx.transaction_id}
- User: {tx.user_id}
- Amount: {tx.amount} {tx.currency}
- Type: {tx.transaction_type}
- Merchant: {tx.merchant_name or 'N/A'} ({tx.merchant_category or 'N/A'})
- Location: {tx.location_city or ''}, {tx.location_country}
- Device ID: {tx.device_id or 'unknown'}
- IP Address: {tx.ip_address or 'unknown'}
- New Device: {tx.is_new_device}
- Time since last transaction: {tx.previous_transaction_minutes_ago or 'N/A'} minutes
- User's average transaction: ${tx.user_avg_transaction or 'N/A'}
- Account age: {tx.account_age_days or 'N/A'} days

FRAUD INDICATORS TO CHECK:
1. Unusual transaction amount (far above user average)
2. Location mismatch or unusual geography
3. Multiple rapid transactions (velocity)
4. Unknown device or suspicious IP
5. New account with high-value transaction
6. Suspicious merchant category

Respond ONLY with valid JSON in this exact format:
{{
  "fraud_risk_score": <integer 0-100>,
  "risk_level": "<LOW|MEDIUM|HIGH|CRITICAL>",
  "fraud_indicators": ["<indicator1>", "<indicator2>"],
  "behavioural_analysis": "<2-3 sentence analysis>",
  "recommendation": "<APPROVE|REVIEW|BLOCK>"
}}"""

    async def analyze(self, tx: Transaction) -> dict:
        if not self.model:
            return self._fallback_analysis(tx)

        try:
            response = self.model.generate_content(self._build_prompt(tx))
            text = response.text.strip()
            if "```" in text:
                text = text.split("```")[1].replace("json", "").strip()
            result = json.loads(text)
            result["agent"] = self.name
            return result
        except Exception as e:
            return self._fallback_analysis(tx)

    def _fallback_analysis(self, tx: Transaction) -> dict:
        """Rule-based fallback if AI is unavailable."""
        score = 0
        indicators = []

        if tx.user_avg_transaction and tx.amount > tx.user_avg_transaction * 5:
            score += 35
            indicators.append("Amount significantly above user average")

        if tx.is_new_device:
            score += 20
            indicators.append("Transaction from unrecognized device")

        if tx.previous_transaction_minutes_ago and tx.previous_transaction_minutes_ago < 2:
            score += 25
            indicators.append("Rapid successive transactions detected")

        if tx.account_age_days and tx.account_age_days < 30 and tx.amount > 1000:
            score += 20
            indicators.append("New account with high-value transaction")

        high_risk_countries = ["XX", "ZZ"]
        if tx.location_country in high_risk_countries:
            score += 20
            indicators.append("Transaction from high-risk geography")

        score = min(score, 100)
        risk_level = "LOW" if score < 30 else "MEDIUM" if score < 60 else "HIGH" if score < 85 else "CRITICAL"
        recommendation = "APPROVE" if score < 40 else "REVIEW" if score < 70 else "BLOCK"

        return {
            "agent": self.name,
            "fraud_risk_score": score,
            "risk_level": risk_level,
            "fraud_indicators": indicators or ["No significant fraud indicators detected"],
            "behavioural_analysis": f"Rule-based analysis yielded risk score {score}. {len(indicators)} indicator(s) flagged.",
            "recommendation": recommendation
        }
