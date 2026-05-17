"""
SafeNest v2.0 — Webhook Sender
Asynchronously sends transaction analysis results to registered bank webhooks
"""

import asyncio
import aiohttp
import json
import hmac
import hashlib
import time
from typing import Dict, Any, Optional
from webhook_manager import WebhookManager

class WebhookSender:
    def __init__(self, webhook_manager: WebhookManager):
        self.webhook_manager = webhook_manager

    @staticmethod
    def _generate_signature(payload: str, secret: str) -> str:
        """Generate HMAC-SHA256 signature for webhook payload"""
        return hmac.new(
            secret.encode(),
            payload.encode(),
            hashlib.sha256
        ).hexdigest()

    async def send_webhook(self, webhook_url: str, webhook_secret: str, payload: Dict[str, Any]) -> tuple:
        """
        Send webhook to bank endpoint
        Returns: (http_status, response_time_ms)
        """
        start_time = time.time()
        
        try:
            payload_json = json.dumps(payload)
            signature = self._generate_signature(payload_json, webhook_secret)
            
            headers = {
                "Content-Type": "application/json",
                "X-SafeNest-Signature": signature,
                "X-SafeNest-Timestamp": str(int(time.time())),
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    webhook_url,
                    data=payload_json,
                    headers=headers,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    response_time_ms = int((time.time() - start_time) * 1000)
                    return response.status, response_time_ms
                    
        except asyncio.TimeoutError:
            return 408, int((time.time() - start_time) * 1000)
        except Exception as e:
            print(f"❌ Webhook error: {str(e)}")
            return 500, int((time.time() - start_time) * 1000)

    async def broadcast_transaction_result(self, api_key: str, transaction_result: Dict[str, Any]):
        """
        Broadcast transaction analysis result to all registered webhooks for a bank
        """
        webhooks = self.webhook_manager.get_webhooks_for_api_key(api_key)
        
        if not webhooks:
            return {"status": "no_webhooks", "message": "No webhooks registered for this API key"}
        
        # Prepare payload
        payload = {
            "event_type": "transaction_analyzed",
            "timestamp": transaction_result.get("timestamp"),
            "transaction_id": transaction_result.get("transaction_id"),
            "action": transaction_result.get("action"),
            "risk_level": transaction_result.get("risk_level"),
            "final_risk_score": transaction_result.get("final_risk_score"),
            "compliance_status": transaction_result.get("compliance_status"),
            "ctr_required": transaction_result.get("ctr_required"),
            "sar_required": transaction_result.get("sar_required"),
            "processing_time_ms": transaction_result.get("processing_time_ms"),
            "alert_message": transaction_result.get("response", {}).get("alert_message"),
        }
        
        payload_json = json.dumps(payload)
        
        # Send to all webhooks concurrently
        tasks = []
        for webhook in webhooks:
            task = self.send_webhook(
                webhook["webhook_url"],
                webhook["webhook_secret"],
                payload
            )
            tasks.append((webhook["id"], task))
        
        results = []
        for webhook_id, task in tasks:
            try:
                http_status, response_time = await task
                results.append({
                    "webhook_id": webhook_id,
                    "status": http_status,
                    "response_time_ms": response_time,
                    "success": 200 <= http_status < 300
                })
                
                # Log the webhook event
                self.webhook_manager.log_webhook_event(
                    webhook_id,
                    transaction_result.get("transaction_id"),
                    "transaction_analyzed",
                    payload_json,
                    http_status,
                    response_time
                )
                
            except Exception as e:
                results.append({
                    "webhook_id": webhook_id,
                    "status": 500,
                    "error": str(e),
                    "success": False
                })
        
        return {
            "status": "broadcasted",
            "transaction_id": transaction_result.get("transaction_id"),
            "webhooks_sent": len(results),
            "results": results
        }


# Example usage in FastAPI endpoint:
async def trigger_webhooks_example(api_key: str, transaction_result: Dict):
    """
    This would be called after transaction analysis completes
    """
    webhook_manager = WebhookManager()
    sender = WebhookSender(webhook_manager)
    await sender.broadcast_transaction_result(api_key, transaction_result)
