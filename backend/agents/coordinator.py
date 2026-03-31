"""
Coordinator Agent — Orchestrates the full multi-agent workflow.
Manages communication between Sentry, Auditor, and Response agents.
"""
import os
import json
import google.generativeai as genai
from datetime import datetime
from models import Transaction
from agents.sentry import SentryAgent
from agents.auditor import AuditorAgent
from agents.response import ResponseAgent


class CoordinatorAgent:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY", "")
        if api_key:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
        else:
            self.model = None

        self.sentry = SentryAgent()
        self.auditor = AuditorAgent()
        self.response = ResponseAgent()
        self.name = "Coordinator Agent"

    async def process_transaction(self, tx: Transaction) -> dict:
        """
        Full multi-agent pipeline:
        1. Sentry Agent → Fraud Detection
        2. Auditor Agent → Compliance Verification
        3. Response Agent → Automated Action
        4. Coordinator → Final Summary
        """
        pipeline_start = datetime.utcnow()
        agent_timeline = []

        # Step 1: Sentry Agent
        t1 = datetime.utcnow()
        sentry_result = await self.sentry.analyze(tx)
        agent_timeline.append({
            "step": 1,
            "agent": "Sentry Agent",
            "duration_ms": int((datetime.utcnow() - t1).total_seconds() * 1000),
            "result_summary": f"Risk Score: {sentry_result.get('fraud_risk_score')}/100 | {sentry_result.get('risk_level')}"
        })

        # Step 2: Auditor Agent
        t2 = datetime.utcnow()
        auditor_result = await self.auditor.verify(tx, sentry_result)
        agent_timeline.append({
            "step": 2,
            "agent": "Auditor Agent",
            "duration_ms": int((datetime.utcnow() - t2).total_seconds() * 1000),
            "result_summary": f"KYC: {auditor_result.get('kyc_status')} | AML: {auditor_result.get('aml_status')} | {auditor_result.get('compliance_status')}"
        })

        # Step 3: Response Agent
        t3 = datetime.utcnow()
        response_result = await self.response.respond(tx, sentry_result, auditor_result)
        agent_timeline.append({
            "step": 3,
            "agent": "Response Agent",
            "duration_ms": int((datetime.utcnow() - t3).total_seconds() * 1000),
            "result_summary": f"Action: {response_result.get('action_taken')} | Severity: {response_result.get('severity')}"
        })

        # Step 4: Coordinator summary
        coordinator_summary = self._summarize(tx, sentry_result, auditor_result, response_result)

        total_ms = int((datetime.utcnow() - pipeline_start).total_seconds() * 1000)

        return {
            "transaction_id": tx.transaction_id,
            "timestamp": tx.timestamp,
            "coordinator": coordinator_summary,

            # Core fields for dashboard
            "fraud_risk_score": sentry_result.get("fraud_risk_score", 0),
            "risk_level": sentry_result.get("risk_level", "LOW"),
            "action_taken": response_result.get("action_taken", "APPROVE"),
            "compliance_status": auditor_result.get("compliance_status", "COMPLIANT"),
            "severity": response_result.get("severity", "INFO"),

            # Detailed agent results
            "sentry_result": sentry_result,
            "auditor_result": auditor_result,
            "response_result": response_result,

            # Pipeline metadata
            "agent_pipeline": agent_timeline,
            "total_processing_ms": total_ms,
            "processed_by": self.name
        }

    def _summarize(self, tx, sentry, auditor, response) -> dict:
        score = sentry.get("fraud_risk_score", 0)
        action = response.get("action_taken", "APPROVE")

        overall = "SAFE"
        if action == "BLOCK":
            overall = "BLOCKED"
        elif action in ("FLAG_FOR_REVIEW", "REQUIRE_OTP", "REQUIRE_BIOMETRIC"):
            overall = "SUSPICIOUS"
        elif score >= 30:
            overall = "MONITOR"

        return {
            "overall_verdict": overall,
            "summary": f"Transaction {tx.transaction_id} analyzed. Fraud Score: {score}/100. Action: {action}.",
            "key_findings": [
                *sentry.get("fraud_indicators", [])[:2],
                *auditor.get("regulatory_flags", [])[:2],
            ],
            "coordinator_agent": self.name
        }
