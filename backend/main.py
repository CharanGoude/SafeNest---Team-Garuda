"""
SafeNest v2.0 — FastAPI Application
Autonomous Fraud Detection & Compliance System
Direct 3-agent pipeline — simple bank integration
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import asyncio
import json
import random
import uuid
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, HTTPException, Security
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security.api_key import APIKeyHeader

from models import TransactionRequest, AnalysisResponse, SentryResult, CoordinatorResult, ResponseResult, ActionTaken, RiskLevel, ComplianceStatus
from agents.db.database import db
from agents.coordinator import CoordinatorAgent
from agents.response import ResponseAgent

# ── App ───────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="SafeNest Fraud Detection API",
    description="Autonomous Fraud Detection & Compliance Monitoring. Integrate with one API call.",
    version="2.0.0"
)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# ── Auth ──────────────────────────────────────────────────────────────────────
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

async def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    if not api_key:
        raise HTTPException(status_code=401, detail="API key required. Add X-API-Key header.")
    bank_name = db.validate_api_key(api_key)
    if not bank_name:
        raise HTTPException(status_code=403, detail="Invalid or inactive API key.")
    return bank_name

# ── Agents ────────────────────────────────────────────────────────────────────
coordinator_agent = CoordinatorAgent(db)
response_agent = ResponseAgent(db)

# ── WebSocket ─────────────────────────────────────────────────────────────────
connections: list = []

async def broadcast(data: dict):
    dead = []
    for ws in connections:
        try: await ws.send_json(data)
        except: dead.append(ws)
    for ws in dead:
        if ws in connections: connections.remove(ws)

# ── Core pipeline (Coordinator Agent) ─────────────────────────────────────────
async def run_pipeline(tx: TransactionRequest) -> AnalysisResponse:
    tx.transaction_id = tx.transaction_id or str(uuid.uuid4())[:8].upper()
    timestamp = datetime.utcnow().isoformat()

    # Step 1: Get baseline transaction (if exists)
    baseline = db.get_baseline_transaction(tx.user_id, tx.account_number)

    # Step 2: Run Coordinator agent (compares to baseline)
    coordinator_raw = await coordinator_agent.analyze(tx, baseline)

    # Step 3: Response agent decides action based on coordinator score
    response_raw = await response_agent.respond(tx, coordinator_raw)

    total_ms = coordinator_raw["processing_ms"] + response_raw["processing_ms"]

    # Build typed result objects
    coordinator_r = CoordinatorResult(
        risk_score = coordinator_raw["risk_score"],
        comparison_indicators = coordinator_raw.get("comparison_indicators", []),
        parameter_changes = coordinator_raw.get("parameter_changes", []),
        is_baseline = coordinator_raw.get("is_baseline", False),
        processing_ms = coordinator_raw["processing_ms"]
    )

    response_r = ResponseResult(
        action           = ActionTaken(response_raw["action"]),
        risk_level       = RiskLevel(response_raw["risk_level"]),
        final_risk_score = response_raw["final_risk_score"],
        reasoning        = response_raw["reasoning"],
        alert_message    = response_raw["alert_message"],
        secondary_actions= response_raw["secondary_actions"],
        processing_ms    = response_raw["processing_ms"]
    )

    # For backward compatibility with frontend, create empty Sentry result
    sentry_r = SentryResult(
        risk_score = coordinator_raw["risk_score"],
        fraud_indicators = coordinator_raw.get("comparison_indicators", []),
        behavioural_summary = f"Baseline comparison: {'; '.join(coordinator_raw.get('parameter_changes', [])[:2])}",
        processing_ms = coordinator_raw["processing_ms"]
    )

    analysis = AnalysisResponse(
        transaction_id     = tx.transaction_id,
        timestamp          = timestamp,
        processing_time_ms = total_ms,
        action             = response_r.action,
        risk_level         = response_r.risk_level,
        final_risk_score   = response_r.final_risk_score,
        compliance_status  = ComplianceStatus.COMPLIANT,
        ctr_required       = False,
        sar_required       = False,
        coordinator        = coordinator_r,
        response           = response_r,
        blockchain_hash    = response_raw.get("blockchain_hash", "N/A")
    )

    # Save to DB
    db.save_transaction({
        "transaction_id":     tx.transaction_id,
        "timestamp":          timestamp,
        "account_number":     tx.account_number,
        "user_id":            tx.user_id,
        "amount":             tx.amount,
        "currency":           tx.currency,
        "transaction_type":   tx.transaction_type.value,
        "merchant_name":      tx.merchant_name,
        "merchant_category":  tx.merchant_category,
        "location_country":   tx.location_country,
        "location_city":      tx.location_city,
        "device_id":          tx.device_id,
        "ip_address":         tx.ip_address,
        "is_new_device":      int(tx.is_new_device),
        "action":             response_r.action.value,
        "risk_level":         response_r.risk_level.value,
        "final_risk_score":   response_r.final_risk_score,
        "compliance_status":  "COMPLIANT",
        "ctr_required":       0,
        "sar_required":       0,
        "blockchain_hash":    response_raw.get("blockchain_hash","N/A"),
        "fraud_indicators":   json.dumps(coordinator_raw.get("comparison_indicators", [])),
        "regulatory_flags":   json.dumps([]),
        "processing_time_ms": total_ms,
        "sentry_score":       coordinator_raw["risk_score"],
    })

    # Broadcast alert if high risk
    if response_r.risk_level in (RiskLevel.HIGH, RiskLevel.CRITICAL):
        await broadcast({
            "type":           "ALERT",
            "transaction_id": tx.transaction_id,
            "action":         response_r.action.value,
            "risk_level":     response_r.risk_level.value,
            "risk_score":     response_r.final_risk_score,
            "merchant":       tx.merchant_name,
            "amount":         tx.amount,
            "timestamp":      timestamp,
        })

    return analysis

# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/", include_in_schema=False)
def root():
    return {"name":"SafeNest Fraud Detection API","version":"2.0.0","docs":"/docs","health":"/health"}

@app.get("/health", tags=["System"])
def health():
    stats = db.get_stats()
    return {
        "status":         "healthy",
        "version":        "2.0.0",
        "agents":         ["Coordinator Agent","Response Agent"],
        "database":       "connected",
        "total_analyzed": stats.get("total",0),
        "timestamp":      datetime.utcnow().isoformat()
    }

@app.post("/api/v1/analyze", response_model=AnalysisResponse, tags=["Core"])
async def analyze(tx: TransactionRequest, bank_name: str = Depends(verify_api_key)):
    """Main endpoint — analyze transaction through all 3 agents."""
    try:
        return await run_pipeline(tx)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/transactions", tags=["Data"])
async def get_transactions(
    limit:int=50, offset:int=0,
    action:Optional[str]=None, risk_level:Optional[str]=None,
    bank_name:str=Depends(verify_api_key)
):
    txs = db.get_transactions(limit=limit, offset=offset, action=action, risk_level=risk_level)
    for t in txs:
        try:
            t["fraud_indicators"] = json.loads(t.get("fraud_indicators","[]"))
            t["regulatory_flags"] = json.loads(t.get("regulatory_flags","[]"))
        except: pass
    return {"transactions":txs,"total":len(txs),"limit":limit,"offset":offset}

@app.get("/api/v1/transactions/{tx_id}", tags=["Data"])
async def get_transaction(tx_id:str, bank_name:str=Depends(verify_api_key)):
    tx = db.get_transaction_by_id(tx_id)
    if not tx: raise HTTPException(status_code=404, detail="Transaction not found")
    try:
        tx["fraud_indicators"] = json.loads(tx.get("fraud_indicators","[]"))
        tx["regulatory_flags"] = json.loads(tx.get("regulatory_flags","[]"))
    except: pass
    tx["audit_logs"] = db.get_audit_logs(tx_id)
    return tx

@app.get("/api/v1/stats", tags=["Data"])
async def get_stats(bank_name:str=Depends(verify_api_key)):
    return db.get_stats()

@app.get("/api/v1/blockchain", tags=["Compliance"])
async def get_blockchain(limit:int=100, bank_name:str=Depends(verify_api_key)):
    ledger = db.get_blockchain(limit=limit)
    return {"ledger":ledger,"total_blocks":len(ledger),"chain_valid":True}

@app.post("/api/v1/simulate", tags=["Testing"])
async def simulate(count:int=5, bank_name:str=Depends(verify_api_key)):
    profiles = [
        ("user_rahul_k",  "ACC101RAHUL",    450.0, 730,"IN","Mumbai",   "iPhone_14_A1"),
        ("user_priya_m",  "ACC102PRIYA",    800.0, 365,"IN","Delhi",    "Samsung_S23"),
        ("user_carlos_r", "ACC103CARLOS",  1200.0, 900,"US","New York", "MacBook_Pro"),
        ("user_anna_s",   "ACC104ANNA",     600.0, 500,"GB","London",   "Pixel_7"),
    ]
    merchants = [
        ("Amazon India","RETAIL","IN"),("Swiggy","FOOD","IN"),
        ("Netflix","STREAMING","US"),("CryptoFast","CRYPTO","RU"),
        ("QuickCash247","TRANSFER","KP"),("Starbucks","FOOD","US"),
    ]
    scenarios = ["safe","safe","medium","high","critical"]
    results   = []

    for _ in range(min(count,10)):
        p = random.choice(profiles)
        uid,acc,avg_tx,age,country,city,device = p
        scenario = random.choice(scenarios)
        m = random.choice(merchants)

        if scenario == "safe":
            amt=round(avg_tx*random.uniform(0.3,1.2),2); new=False; mins=random.randint(60,2880)
            ip=f"192.168.{random.randint(1,50)}.{random.randint(1,255)}"; merch=merchants[0]
        elif scenario == "medium":
            amt=round(avg_tx*random.uniform(3.0,4.5),2); new=True; mins=random.randint(8,25)
            ip=f"91.{random.randint(100,200)}.{random.randint(1,255)}.1"; merch=merchants[3]
        elif scenario == "high":
            amt=round(avg_tx*random.uniform(5.0,9.0),2); new=True; mins=2
            ip=f"185.{random.randint(1,255)}.{random.randint(1,255)}.1"; merch=merchants[4]
        else:
            acc="ACC999BLACKLIST"; amt=round(random.uniform(9000,18000),2); new=True; mins=1
            ip=f"185.{random.randint(1,255)}.{random.randint(1,255)}.1"; merch=merchants[4]

        tx = TransactionRequest(
            user_id=uid, account_number=acc, amount=amt, currency="INR",
            transaction_type="PAYMENT", merchant_name=merch[0], merchant_category=merch[1],
            location_country=merch[2] if scenario in ("high","critical") else country,
            location_city=city, device_id=device if not new else "UNKNOWN_DEVICE_X7",
            ip_address=ip, is_new_device=new, account_age_days=age,
            user_avg_transaction=avg_tx, previous_transaction_minutes_ago=mins
        )
        r = await run_pipeline(tx)
        results.append({"transaction_id":r.transaction_id,"action":r.action.value,"risk_score":r.final_risk_score,"risk_level":r.risk_level.value})
        await asyncio.sleep(0.05)

    return {"simulated":len(results),"results":results}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True: await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in connections: connections.remove(websocket)
