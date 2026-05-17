"""
SafeNest v2.0 — Webhook API Endpoints
Add these endpoints to main.py for webhook management
"""

from fastapi import APIRouter, HTTPException, Depends, Security
from pydantic import BaseModel
from typing import List, Dict, Any
from webhook_manager import WebhookManager

webhook_router = APIRouter(prefix="/api/v1/webhooks", tags=["Webhooks"])
webhook_manager = WebhookManager()

# ── Pydantic Models ──────────────────────────────────────────────────────────

class RegisterWebhookRequest(BaseModel):
    bank_name: str
    webhook_url: str
    webhook_secret: str

class WebhookInfo(BaseModel):
    webhook_id: int
    bank_name: str
    webhook_url: str
    is_active: bool
    success_count: int
    failure_count: int
    last_triggered: str | None

class WebhookStats(BaseModel):
    total_webhooks: int
    total_success: int
    total_failure: int
    success_rate: float

# ── API Endpoints ──────────────────────────────────────────────────────────

@webhook_router.post("/register")
async def register_webhook(
    request: RegisterWebhookRequest,
    api_key: str = Security(verify_api_key)  # From main.py
) -> Dict[str, Any]:
    """
    Register a webhook endpoint for transaction notifications
    
    Bank provides:
    - webhook_url: HTTPS endpoint to receive notifications
    - webhook_secret: Secret for HMAC signature verification
    
    Returns:
    - webhook_id: Unique ID for this webhook
    
    Webhook will receive POST requests with:
    - Headers: X-SafeNest-Signature, X-SafeNest-Timestamp
    - Body: Transaction analysis result (JSON)
    """
    result = webhook_manager.register_webhook(
        bank_name=request.bank_name,
        api_key=api_key,
        webhook_url=request.webhook_url,
        webhook_secret=request.webhook_secret
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@webhook_router.get("/list")
async def list_webhooks(
    api_key: str = Security(verify_api_key)
) -> List[WebhookInfo]:
    """
    List all registered webhooks for this API key
    """
    webhooks = webhook_manager.get_webhooks_for_api_key(api_key)
    return [WebhookInfo(**w) for w in webhooks]

@webhook_router.get("/stats")
async def webhook_stats(
    api_key: str = Security(verify_api_key)
) -> WebhookStats:
    """
    Get webhook statistics and success rates
    """
    stats = webhook_manager.get_webhook_stats(api_key)
    return WebhookStats(**stats)

@webhook_router.delete("/{webhook_id}")
async def deactivate_webhook(
    webhook_id: int,
    api_key: str = Security(verify_api_key)
) -> Dict[str, str]:
    """
    Deactivate a webhook (stop receiving notifications)
    """
    result = webhook_manager.deactivate_webhook(webhook_id)
    
    if result["status"] == "error":
        raise HTTPException(status_code=404, detail=result["message"])
    
    return result

@webhook_router.get("/admin/all", tags=["Admin"])
async def get_all_webhooks_admin(
    api_key: str = Security(verify_api_key)
) -> List[Dict]:
    """
    ADMIN ONLY: Get all webhooks across all banks
    """
    # Check if this is an admin API key (implement your own logic)
    if not api_key.startswith("sk-admin"):
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return webhook_manager.list_all_webhooks()


# ── Integration Example ──────────────────────────────────────────────────────
"""
To integrate these endpoints into main.py:

1. Import at top of main.py:
   from webhook_api import webhook_router
   from webhook_sender import WebhookSender
   from webhook_manager import WebhookManager

2. Add to FastAPI app:
   app.include_router(webhook_router)

3. After transaction analysis, send webhooks:
   webhook_sender = WebhookSender(WebhookManager())
   await webhook_sender.broadcast_transaction_result(api_key, analysis_result)

4. Modify the /api/v1/analyze endpoint to:
   
   @app.post("/api/v1/analyze")
   async def analyze(request: TransactionRequest, bank_name: str = Depends(verify_api_key)):
       # ... existing analysis code ...
       
       # Add webhook broadcast
       webhook_sender = WebhookSender(WebhookManager())
       webhook_result = await webhook_sender.broadcast_transaction_result(
           api_key=request.headers.get("X-API-Key"),
           transaction_result=result
       )
       
       return result
"""
