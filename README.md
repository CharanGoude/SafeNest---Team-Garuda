# 🛡️ SafeNest — Autonomous Fraud-Guard & Compliance Orchestrator
**Team Garuda | Virtusa Jatayuvu Season 5 | Stage 2**

---

## ⚡ Quick Start (2 terminals)

### Terminal 1 — Backend
```bash
cd safenest/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
→ API live at http://localhost:8000  
→ Swagger docs at http://localhost:8000/docs

### Terminal 2 — Frontend
```bash
cd safenest/frontend
npm install
npm run dev
```
→ Dashboard at http://localhost:3000

---

## 🤖 4 AI Agents

| Agent | Role | Tech |
|-------|------|------|
| **Coordinator** | Orchestrates the pipeline, combines scores | Python async |
| **Sentry** | Fraud pattern detection + risk scoring | Gemini AI + Rules |
| **Auditor** | KYC / AML / Watchlist compliance | Gemini AI + Rules |
| **Response** | Automated mitigation actions | Gemini AI + Rules |

> **Works without an API key!** All agents have intelligent rule-based fallback logic.  
> To enable Gemini AI: create `backend/.env` with `GOOGLE_API_KEY=your_key`

---

## 🎯 Risk Thresholds

| Score | Action |
|-------|--------|
| 0–29  | ✅ APPROVE |
| 30–49 | ⚑ FLAG FOR REVIEW |
| 50–69 | 📱 REQUIRE OTP / BIOMETRIC |
| 70–89 | 🔒 FREEZE ACCOUNT |
| 90–100| 🚫 BLOCK + NOTIFY + REPORT |

---

## 📡 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET`  | `/health` | System status |
| `POST` | `/analyze` | Run transaction through all 4 agents |
| `GET`  | `/transactions?limit=50` | Transaction history |
| `GET`  | `/stats` | Dashboard statistics |
| `POST` | `/simulate?count=5` | Generate demo transactions |
| `WS`   | `/ws` | Real-time alert stream |

---

## 📁 Project Structure

```
safenest/
├── backend/
│   ├── main.py               ← FastAPI app + all routes
│   ├── models.py             ← Transaction & data models
│   ├── requirements.txt
│   ├── .env.example          ← Add GOOGLE_API_KEY here
│   └── agents/
│       ├── coordinator.py    ← Orchestrates all agents
│       ├── sentry.py         ← Fraud detection (Gemini + rules)
│       ├── auditor.py        ← KYC/AML (Gemini + rules)
│       └── response.py       ← Auto-mitigation (Gemini + rules)
└── frontend/
    ├── src/
    │   ├── App.jsx           ← Layout, sidebar, WebSocket alerts
    │   ├── index.css         ← Dark cyberpunk theme
    │   └── pages/
    │       ├── Dashboard.jsx        ← Stats overview + agent diagram
    │       ├── AnalyzePage.jsx      ← TX form + real-time agent trace
    │       ├── TransactionsPage.jsx ← Full log with detail panel
    │       └── BlockchainPage.jsx   ← Immutable compliance ledger
    ├── package.json
    └── vite.config.js
```

---

## 🔬 Test Scenarios (on Analyze page)

Use the **Quick Presets** on the Analyze page:
- 🟢 **Safe TX** — small amount, known merchant, old account
- 🟡 **Suspicious** — near-threshold amount, new device, risky country  
- 🔴 **High Risk** — blacklisted account + critical jurisdiction + rapid TX
