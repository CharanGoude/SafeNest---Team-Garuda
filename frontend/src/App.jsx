import { useState, useEffect, useRef } from "react";
import Dashboard from "./pages/Dashboard";
import AnalyzePage from "./pages/AnalyzePage";
import BlockchainPage from "./pages/BlockchainPage";
import TransactionsPage from "./pages/TransactionsPage";
import "./index.css";

const NAV = [
  { id: "dashboard", label: "Dashboard", icon: "◈" },
  { id: "analyze", label: "Analyze TX", icon: "⬡" },
  { id: "transactions", label: "Transactions", icon: "≋" },
  { id: "blockchain", label: "Ledger", icon: "⬡" },
];

export default function App() {
  const [page, setPage] = useState("dashboard");
  const [liveAlert, setLiveAlert] = useState(null);
  const wsRef = useRef(null);

  useEffect(() => {
    const connect = () => {
      try {
        const ws = new WebSocket("ws://localhost:8000/ws");
        ws.onmessage = (e) => {
          const msg = JSON.parse(e.data);
          if (msg.type === "new_transaction" && msg.data.severity !== "LOW") {
            setLiveAlert(msg.data);
            setTimeout(() => setLiveAlert(null), 5000);
          }
        };
        ws.onclose = () => setTimeout(connect, 3000);
        wsRef.current = ws;
      } catch(e) {}
    };
    connect();
    return () => wsRef.current?.close();
  }, []);

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg)", fontFamily: "'Space Mono', monospace" }}>
      <aside style={{
        width: 220, background: "var(--surface)", borderRight: "1px solid var(--border)",
        display: "flex", flexDirection: "column", padding: "24px 0", position: "fixed",
        height: "100vh", zIndex: 100
      }}>
        <div style={{ padding: "0 24px 32px" }}>
          <div style={{ fontSize: 10, color: "var(--accent)", letterSpacing: 4, marginBottom: 4, fontFamily: "'Syne', sans-serif" }}>AUTONOMOUS</div>
          <div style={{ fontSize: 22, fontWeight: 800, color: "var(--text)", letterSpacing: 1, fontFamily: "'Syne', sans-serif" }}>SafeNest</div>
          <div style={{ fontSize: 9, color: "var(--muted)", marginTop: 2, letterSpacing: 2 }}>FRAUD-GUARD v1.0</div>
        </div>

        <div style={{ flex: 1 }}>
          {NAV.map(n => (
            <button key={n.id} onClick={() => setPage(n.id)} style={{
              display: "flex", alignItems: "center", gap: 12, width: "100%",
              padding: "13px 24px", border: "none", cursor: "pointer", textAlign: "left",
              background: page === n.id ? "rgba(0,255,136,0.07)" : "transparent",
              color: page === n.id ? "var(--accent)" : "var(--muted)",
              borderLeft: page === n.id ? "2px solid var(--accent)" : "2px solid transparent",
              fontSize: 11, letterSpacing: 2, fontFamily: "inherit", transition: "all 0.2s"
            }}>
              <span style={{ fontSize: 14 }}>{n.icon}</span>
              {n.label.toUpperCase()}
            </button>
          ))}
        </div>

        <div style={{ padding: "16px 24px", borderTop: "1px solid var(--border)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
            <div style={{ width: 7, height: 7, borderRadius: "50%", background: "var(--accent)", boxShadow: "0 0 8px var(--accent)", animation: "pulse 2s infinite" }} />
            <span style={{ fontSize: 9, color: "var(--accent)", letterSpacing: 2 }}>4 AGENTS ONLINE</span>
          </div>
          {["Coordinator", "Sentry", "Auditor", "Response"].map(a => (
            <div key={a} style={{ fontSize: 9, color: "var(--muted)", letterSpacing: 1, marginBottom: 3 }}>◉ {a}</div>
          ))}
        </div>
      </aside>

      <main style={{ marginLeft: 220, flex: 1, padding: "32px", minHeight: "100vh" }}>
        {page === "dashboard" && <Dashboard onNavigate={setPage} />}
        {page === "analyze" && <AnalyzePage />}
        {page === "transactions" && <TransactionsPage />}
        {page === "blockchain" && <BlockchainPage />}
      </main>

      {liveAlert && (
        <div style={{
          position: "fixed", bottom: 24, right: 24, background: "var(--surface)",
          border: `1px solid ${liveAlert.severity === "CRITICAL" ? "var(--danger)" : "var(--warning)"}`,
          borderRadius: 8, padding: "16px 20px", maxWidth: 320, zIndex: 999,
          boxShadow: `0 0 24px ${liveAlert.severity === "CRITICAL" ? "rgba(255,59,59,0.3)" : "rgba(255,170,0,0.3)"}`,
          animation: "slideIn 0.3s ease"
        }}>
          <div style={{ fontSize: 10, color: liveAlert.severity === "CRITICAL" ? "var(--danger)" : "var(--warning)", letterSpacing: 2, marginBottom: 6 }}>
            ⚠ LIVE ALERT — {liveAlert.severity}
          </div>
          <div style={{ fontSize: 12, color: "var(--text)", fontWeight: 700 }}>TX #{liveAlert.transaction_id}</div>
          <div style={{ fontSize: 11, color: "var(--muted)", marginTop: 4 }}>{liveAlert.action?.replace(/_/g, " ")}</div>
        </div>
      )}
    </div>
  );
}
