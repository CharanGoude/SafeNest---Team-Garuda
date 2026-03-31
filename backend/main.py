"""
SafeNest - Autonomous Fraud-Guard & Compliance Orchestrator
FastAPI Backend — Full Agentic Pipeline v2.1
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from models import Transaction
from agents.coordinator import CoordinatorAgent
import asyncio, random, uuid
from datetime import datetime, timedelta

app = FastAPI(title="SafeNest API", version="2.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

coordinator = CoordinatorAgent()
transaction_history = []
connected_websockets = []

# ── Realistic simulation data ────────────────────────────────────────────────

SIMULATION_PROFILES = [
    # (user_id, account, avg_tx, age_days, usual_country, usual_city)
    ("user_rahul_k",   "ACC101RAHUL",  450.0,  730, "IN", "Hyderabad"),
    ("user_priya_m",   "ACC102PRIYA",  800.0,  365, "IN", "Mumbai"),
    ("user_carlos_r",  "ACC103CARLOS", 1200.0, 900, "US", "New York"),
    ("user_anna_s",    "ACC104ANNA",   600.0,  500, "GB", "London"),
    ("user_wei_l",     "ACC105WEI",    2000.0, 180, "SG", "Singapore"),
    ("user_blacklist", "ACC999BLACKLIST", 500.0, 200, "IN", "Delhi"),  # always triggers
]

MERCHANT_PROFILES = [
    ("Swiggy",          "FOOD_DELIVERY",  50,    500,   "IN"),
    ("Amazon India",    "RETAIL",         200,   5000,  "IN"),
    ("Flipkart",        "RETAIL",         150,   3000,  "IN"),
    ("Netflix",         "STREAMING",      650,   700,   "US"),
    ("Zomato",          "FOOD_DELIVERY",  80,    300,   "IN"),
    ("Uber",            "RIDE_SHARE",     120,   400,   "IN"),
    ("HDFC Bank ATM",   "WITHDRAWAL",     5000,  20000, "IN"),
    ("Steam Games",     "GAMING",         800,   1500,  "US"),
    ("CryptoFast",      "CRYPTO",         8000,  15000, "RU"),   # high risk
    ("QuickCash247",    "TRANSFER",       9500,  18000, "KP"),   # high risk
    ("AnonPay",         "TRANSFER",       12000, 20000, "IR"),   # high risk
    ("Starbucks",       "FOOD_DELIVERY",  300,   600,   "US"),
    ("Apple Store",     "RETAIL",         999,   2000,  "US"),
    ("Paytm",           "TRANSFER",       500,   1000,  "IN"),
    ("PhonePe",         "TRANSFER",       800,   2000,  "IN"),
]

SCENARIO_WEIGHTS = [
    "safe", "safe", "safe",        # 3x safe (most transactions are legit)
    "medium", "medium",            # 2x medium
    "high",                        # 1x high
    "critical",                    # 1x critical
]

def generate_realistic_transaction():
    scenario = random.choice(SCENARIO_WEIGHTS)
    profile  = random.choice(SIMULATION_PROFILES[:5])  # exclude blacklist for non-critical
    user_id, account, avg_tx, age_days, usual_country, usual_city = profile

    if scenario == "safe":
        # Normal transaction for this user
        merchant = random.choice([m for m in MERCHANT_PROFILES if m[4] == usual_country and m[1] not in ("CRYPTO","TRANSFER")])
        return Transaction(
            user_id=user_id, account_number=account,
            amount=round(random.uniform(avg_tx * 0.3, avg_tx * 1.2), 2),
            currency="USD", transaction_type="PAYMENT",
            merchant_name=merchant[0], merchant_category=merchant[1],
            location_country=usual_country, location_city=usual_city,
            device_id=f"{user_id}_phone", ip_address=f"192.168.{random.randint(1,50)}.{random.randint(1,255)}",
            is_new_device=False,
            previous_transaction_minutes_ago=random.randint(60, 2880),
            user_avg_transaction=avg_tx, account_age_days=age_days
        )

    elif scenario == "medium":
        # Slightly unusual — different city, elevated amount
        merchant = random.choice(MERCHANT_PROFILES[:8])
        countries = ["IN", "US", "GB", "AE", "SG"]
        country = random.choice([c for c in countries if c != usual_country])
        return Transaction(
            user_id=user_id, account_number=account,
            amount=round(avg_tx * random.uniform(2.0, 3.5), 2),
            currency="USD", transaction_type=random.choice(["PAYMENT", "TRANSFER"]),
            merchant_name=merchant[0], merchant_category=merchant[1],
            location_country=country, location_city="Unknown City",
            device_id=f"{user_id}_phone",
            ip_address=f"91.{random.randint(100,200)}.{random.randint(1,255)}.{random.randint(1,255)}",
            is_new_device=True,
            previous_transaction_minutes_ago=random.randint(5, 30),
            user_avg_transaction=avg_tx, account_age_days=age_days
        )

    elif scenario == "high":
        # High risk — suspicious merchant, large amount, rapid tx
        merchant = random.choice([m for m in MERCHANT_PROFILES if m[1] in ("CRYPTO", "TRANSFER")])
        return Transaction(
            user_id=user_id, account_number=account,
            amount=round(random.uniform(avg_tx * 4, avg_tx * 8), 2),
            currency="USD", transaction_type="TRANSFER",
            merchant_name=merchant[0], merchant_category=merchant[1],
            location_country=merchant[4], location_city="Unknown",
            device_id="UNKNOWN_DEVICE_X7",
            ip_address=f"185.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            is_new_device=True,
            previous_transaction_minutes_ago=random.randint(1, 4),
            user_avg_transaction=avg_tx, account_age_days=age_days
        )

    else:  # critical — blacklisted account
        merchant = random.choice([m for m in MERCHANT_PROFILES if m[1] in ("CRYPTO", "TRANSFER")])
        return Transaction(
            user_id="user_blacklist", account_number="ACC999BLACKLIST",
            amount=round(random.uniform(9000, 19000), 2),
            currency="USD", transaction_type="WITHDRAWAL",
            merchant_name=merchant[0], merchant_category=merchant[1],
            location_country=merchant[4], location_city="Unknown",
            device_id="UNKNOWN_DEVICE_CRITICAL",
            ip_address=f"185.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
            is_new_device=True,
            previous_transaction_minutes_ago=1,
            user_avg_transaction=500.0, account_age_days=200
        )

# ── Routes ───────────────────────────────────────────────────────────────────

@app.get("/health")
def health():
    return {
        "status": "operational", "version": "2.1.0",
        "agents": ["Coordinator Agent", "Sentry Agent", "Auditor Agent", "Response Agent"],
        "ai_powered": True, "timestamp": datetime.utcnow().isoformat()
    }

@app.post("/analyze")
async def analyze(tx: Transaction):
    tx.transaction_id = tx.transaction_id or str(uuid.uuid4())[:8].upper()
    tx.timestamp = tx.timestamp or datetime.utcnow().isoformat()

    result = await coordinator.process_transaction(tx)

    record = {
        "transaction_id": tx.transaction_id,
        "timestamp": tx.timestamp,
        "user_id": tx.user_id,
        "account_number": tx.account_number,
        "amount": tx.amount,
        "currency": tx.currency,
        "transaction_type": tx.transaction_type,
        "merchant": tx.merchant_name or "N/A",
        "merchant_category": tx.merchant_category or "N/A",
        "location": f"{tx.location_city or ''}, {tx.location_country}".strip(", "),
        "location_country": tx.location_country,
        "is_new_device": tx.is_new_device,
        "fraud_risk_score": result.get("fraud_risk_score", 0),
        "risk_level": result.get("risk_level", "LOW"),
        "action_taken": result.get("action_taken", "APPROVE"),
        "compliance_status": result.get("compliance_status", "COMPLIANT"),
        "severity": result.get("severity", "INFO"),
        "sentry": result.get("sentry_result", {}),
        "auditor": result.get("auditor_result", {}),
        "response": result.get("response_result", {}),
        "coordinator": result.get("coordinator", {}),
        "agent_pipeline": result.get("agent_pipeline", []),
        "total_processing_ms": result.get("total_processing_ms", 0),
    }
    transaction_history.insert(0, record)
    if len(transaction_history) > 200:
        transaction_history.pop()

    if record["severity"] != "INFO":
        for ws in connected_websockets[:]:
            try:
                await ws.send_json({"type": "new_transaction", "data": record})
            except:
                connected_websockets.remove(ws)

    return record

@app.get("/transactions")
def get_transactions(limit: int = 50):
    return {"transactions": transaction_history[:limit], "total": len(transaction_history)}

@app.get("/stats")
def get_stats():
    if not transaction_history:
        return {"total":0,"approved":0,"blocked":0,"flagged":0,"otp":0,
                "avg_risk":0.0,"critical_count":0,"warning_count":0,
                "fraud_rate":0.0,"total_protected":0.0}
    total    = len(transaction_history)
    approved = sum(1 for t in transaction_history if t["action_taken"] == "APPROVE")
    blocked  = sum(1 for t in transaction_history if t["action_taken"] in ("BLOCK","FREEZE_ACCOUNT"))
    flagged  = sum(1 for t in transaction_history if t["action_taken"] == "FLAG_FOR_REVIEW")
    otp      = sum(1 for t in transaction_history if t["action_taken"] in ("REQUIRE_OTP","REQUIRE_BIOMETRIC"))
    critical = sum(1 for t in transaction_history if t["severity"] == "CRITICAL")
    warning  = sum(1 for t in transaction_history if t["severity"] == "WARNING")
    avg_risk = sum(t["fraud_risk_score"] for t in transaction_history) / total
    protected= sum(t.get("response",{}).get("estimated_prevention_value",0) or 0 for t in transaction_history)
    return {
        "total":total,"approved":approved,"blocked":blocked,"flagged":flagged,"otp":otp,
        "avg_risk":round(avg_risk,1),"critical_count":critical,"warning_count":warning,
        "fraud_rate":round((total-approved)/total*100,1),
        "total_protected":round(protected,2)
    }

@app.post("/simulate")
async def simulate(count: int = 6):
    results = []
    for _ in range(count):
        tx  = generate_realistic_transaction()
        res = await analyze(tx)
        results.append({
            "transaction_id": res["transaction_id"],
            "user": res["user_id"],
            "merchant": res["merchant"],
            "amount": res["amount"],
            "action": res["action_taken"],
            "risk_score": res["fraud_risk_score"],
            "severity": res["severity"]
        })
        await asyncio.sleep(0.08)
    return {"simulated": count, "results": results}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_websockets.append(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        if websocket in connected_websockets:
            connected_websockets.remove(websocket)
