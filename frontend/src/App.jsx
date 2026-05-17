import { useState, useEffect, useRef } from "react";
import Dashboard        from "./pages/Dashboard";
import AnalyzePage      from "./pages/AnalyzePage";
import TransactionsPage from "./pages/TransactionsPage";
import BlockchainPage   from "./pages/BlockchainPage";
import { createWebSocket } from "./utils/api";
import "./index.css";

const NAV = [
  { id:"dashboard",    label:"Dashboard",     icon:"📊" },
  { id:"analyze",      label:"Analyze TX",    icon:"🔍" },
  { id:"transactions", label:"Transactions",  icon:"📋" },
  { id:"blockchain",   label:"Ledger",        icon:"⛓" },
];

export default function App() {
  const [page, setPage]       = useState("dashboard");
  const [alert, setAlert]     = useState(null);
  const [agentStatus, setAgentStatus] = useState("connecting");
  const wsRef = useRef(null);

  useEffect(() => {
    const ws = createWebSocket((msg) => {
      if (msg.type === "ALERT") {
        setAlert(msg);
        setTimeout(() => setAlert(null), 6000);
      }
    });

    wsRef.current = ws;
    ws.onopen    = () => setAgentStatus("online");
    ws.onclose   = () => setAgentStatus("reconnecting");
    ws.onerror   = () => setAgentStatus("error");

    return () => ws.close?.();
  }, []);

  const statusColor = {
    online:       "#16a34a",
    connecting:   "#d97706",
    reconnecting: "#d97706",
    error:        "#dc2626",
  }[agentStatus] || "#94a3b8";

  return (
    <div style={{ display:"flex", minHeight:"100vh", background:"#f8fafc" }}>
      {/* Sidebar */}
      <aside style={{
        width:220, background:"#1e3a5f", display:"flex", flexDirection:"column",
        position:"fixed", height:"100vh", zIndex:100
      }}>
        {/* Logo */}
        <div style={{ padding:"24px 20px 20px" }}>
          <div style={{ display:"flex", alignItems:"center", gap:10, marginBottom:4 }}>
            <div style={{ fontSize:22 }}>🛡️</div>
            <div>
              <div style={{ fontSize:18, fontWeight:800, color:"#fff", letterSpacing:0.5 }}>SafeNest</div>
              <div style={{ fontSize:9, color:"#93c5fd", letterSpacing:1, textTransform:"uppercase" }}>v2.0 · Fraud Guard</div>
            </div>
          </div>
        </div>

        {/* Navigation */}
        <nav style={{ flex:1, padding:"0 10px" }}>
          {NAV.map(n => (
            <button key={n.id} onClick={() => setPage(n.id)} style={{
              display:"flex", alignItems:"center", gap:10, width:"100%",
              padding:"11px 14px", border:"none", cursor:"pointer", textAlign:"left",
              background: page === n.id ? "rgba(255,255,255,0.12)" : "transparent",
              color: page === n.id ? "#fff" : "#93c5fd",
              borderRadius:8, fontSize:13, fontWeight: page===n.id ? 700 : 500,
              fontFamily:"inherit", transition:"all 0.15s", marginBottom:2,
              borderLeft: page===n.id ? "3px solid #60a5fa" : "3px solid transparent",
            }}>
              <span style={{ fontSize:16 }}>{n.icon}</span>
              {n.label}
            </button>
          ))}
        </nav>

        {/* Agent Status */}
        <div style={{ padding:"16px 20px", borderTop:"1px solid rgba(255,255,255,0.08)" }}>
          <div style={{ display:"flex", alignItems:"center", gap:8, marginBottom:10 }}>
            <div style={{ width:8, height:8, borderRadius:"50%", background:statusColor, boxShadow:`0 0 6px ${statusColor}`, animation: agentStatus==="online" ? "pulse 2s infinite" : "none" }} />
            <span style={{ fontSize:10, color:statusColor, textTransform:"uppercase", letterSpacing:1, fontWeight:600 }}>
              Agents {agentStatus}
            </span>
          </div>
          {["Sentry Agent","Auditor Agent","Response Agent"].map(a => (
            <div key={a} style={{ fontSize:10, color:"#93c5fd", marginBottom:4, display:"flex", alignItems:"center", gap:6 }}>
              <span style={{ color:statusColor, fontSize:8 }}>●</span>{a}
            </div>
          ))}
          <div style={{ marginTop:10, padding:"8px 10px", background:"rgba(255,255,255,0.06)", borderRadius:6 }}>
            <div style={{ fontSize:9, color:"#93c5fd", marginBottom:2 }}>DEMO API KEY</div>
            <div style={{ fontSize:9, color:"#fff", fontFamily:"monospace", wordBreak:"break-all" }}>
              sk-safenest-demo-key-2026
            </div>
          </div>
        </div>
      </aside>

      {/* Main content */}
      <main style={{ marginLeft:220, flex:1, padding:"28px 32px", minHeight:"100vh" }}>
        {page === "dashboard"    && <Dashboard onNavigate={setPage} />}
        {page === "analyze"      && <AnalyzePage />}
        {page === "transactions" && <TransactionsPage />}
        {page === "blockchain"   && <BlockchainPage />}
      </main>

      {/* Live Alert Toast */}
      {alert && (
        <div style={{
          position:"fixed", bottom:24, right:24, zIndex:999,
          background:"#fff", borderRadius:10, padding:"16px 20px", maxWidth:320,
          border:`1px solid ${alert.risk_level==="CRITICAL" ? "#fca5a5" : "#fcd34d"}`,
          boxShadow:`0 8px 24px ${alert.risk_level==="CRITICAL" ? "rgba(220,38,38,0.15)" : "rgba(217,119,6,0.15)"}`,
          animation:"slideIn 0.3s ease"
        }}>
          <div style={{ fontSize:10, fontWeight:700, color: alert.risk_level==="CRITICAL" ? "#dc2626" : "#d97706",
            letterSpacing:1, textTransform:"uppercase", marginBottom:6 }}>
            🚨 Live Alert — {alert.risk_level}
          </div>
          <div style={{ fontSize:13, fontWeight:700, color:"#0f172a", marginBottom:2 }}>
            TX #{alert.transaction_id}
          </div>
          <div style={{ fontSize:11, color:"#64748b" }}>
            {alert.merchant} · ${alert.amount?.toFixed(2)}
          </div>
          <div style={{ fontSize:11, color:"#64748b", marginTop:2 }}>
            {alert.action?.replace(/_/g," ")} · Score: {alert.risk_score}/100
          </div>
        </div>
      )}
    </div>
  );
}
