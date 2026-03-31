import { useState, useEffect } from "react";
const API = "http://localhost:8000";

const StatCard = ({ label, value, sub, color = "var(--accent)" }) => (
  <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:10,
    padding:"20px 24px", flex:1, minWidth:140, borderTop:`2px solid ${color}` }}>
    <div style={{ fontSize:9, color:"var(--muted)", letterSpacing:3, marginBottom:10 }}>{label}</div>
    <div style={{ fontSize:28, fontWeight:800, color, fontFamily:"'Syne',sans-serif" }}>{value}</div>
    {sub && <div style={{ fontSize:10, color:"var(--muted)", marginTop:4 }}>{sub}</div>}
  </div>
);

const RiskBar = ({ score }) => {
  const pct = score;
  const color = pct>75?"var(--danger)":pct>50?"var(--warning)":pct>30?"#ffdd57":"var(--accent)";
  return (
    <div style={{ width:"100%", height:4, background:"rgba(255,255,255,0.06)", borderRadius:2, overflow:"hidden" }}>
      <div style={{ height:"100%", width:`${pct}%`, background:color, borderRadius:2, boxShadow:`0 0 6px ${color}` }} />
    </div>
  );
};

const sColor = s => ({ CRITICAL:"var(--danger)", WARNING:"var(--warning)", INFO:"var(--accent)" }[s]||"var(--muted)");
const aIcon  = a => ({ BLOCK:"🔒", FREEZE_ACCOUNT:"🔒", REQUIRE_OTP:"📱", REQUIRE_BIOMETRIC:"🔐",
  FLAG_FOR_REVIEW:"⚑", APPROVE:"✓" }[a]||"?");

export default function Dashboard({ onNavigate }) {
  const [stats, setStats]       = useState(null);
  const [txs, setTxs]           = useState([]);
  const [simulating, setSim]    = useState(false);
  const [error, setError]       = useState(false);

  const fetchAll = async () => {
    try {
      const [s, t] = await Promise.all([
        fetch(`${API}/stats`).then(r=>r.json()),
        fetch(`${API}/transactions?limit=8`).then(r=>r.json()),
      ]);
      setStats(s); setTxs(t.transactions||[]); setError(false);
    } catch { setError(true); }
  };

  useEffect(() => { fetchAll(); const id=setInterval(fetchAll,5000); return ()=>clearInterval(id); }, []);

  const simulate = async () => {
    setSim(true);
    try { await fetch(`${API}/simulate?count=6`,{method:"POST"}); await fetchAll(); } catch{}
    setSim(false);
  };

  return (
    <div>
      {/* Header */}
      <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", marginBottom:32 }}>
        <div>
          <div style={{ fontSize:10, color:"var(--accent)", letterSpacing:4, marginBottom:4 }}>COMMAND CENTER</div>
          <h1 style={{ fontSize:28, fontWeight:800, fontFamily:"'Syne',sans-serif" }}>System Overview</h1>
          <p style={{ fontSize:11, color:"var(--muted)", marginTop:4 }}>Real-time fraud intelligence · 4 AI agents active</p>
        </div>
        <button onClick={simulate} disabled={simulating} style={{
          background:"rgba(0,255,136,0.08)", border:"1px solid var(--accent)", color:"var(--accent)",
          borderRadius:6, padding:"10px 20px", cursor:simulating?"default":"pointer",
          fontFamily:"inherit", fontSize:11, letterSpacing:2
        }}>
          {simulating ? "⟳ RUNNING..." : "▶ SIMULATE 6 TX"}
        </button>
      </div>

      {error && (
        <div style={{ background:"rgba(255,59,59,0.08)", border:"1px solid var(--danger)", borderRadius:8,
          padding:"12px 16px", marginBottom:24, fontSize:11, color:"var(--danger)" }}>
          ⚠ Cannot connect to backend. Run: <code style={{color:"var(--text)"}}>cd backend && uvicorn main:app --reload</code>
        </div>
      )}

      {/* Stats */}
      {stats && (
        <div style={{ display:"flex", gap:14, marginBottom:28, flexWrap:"wrap" }}>
          <StatCard label="TOTAL ANALYZED"   value={stats.total}            sub="all time" />
          <StatCard label="APPROVED"         value={stats.approved}         sub="safe"            color="var(--accent)" />
          <StatCard label="BLOCKED"          value={stats.blocked}          sub="high risk"       color="var(--danger)" />
          <StatCard label="OTP / BIOMETRIC"  value={stats.otp}              sub="challenged"      color="var(--warning)" />
          <StatCard label="FRAUD RATE"       value={`${stats.fraud_rate}%`} sub="of total"        color={stats.fraud_rate>50?"var(--danger)":"var(--warning)"} />
          <StatCard label="AVG RISK SCORE"   value={`${stats.avg_risk}`}    sub="out of 100"      color="var(--accent2)" />
          <StatCard label="VALUE PROTECTED"  value={`$${(stats.total_protected||0).toLocaleString()}`} sub="blocked amount" color="var(--accent)" />
        </div>
      )}

      {/* Agent Pipeline */}
      <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:10, padding:24, marginBottom:24 }}>
        <div style={{ fontSize:10, color:"var(--accent)", letterSpacing:3, marginBottom:20 }}>MULTI-AGENT PIPELINE</div>
        <div style={{ display:"flex", alignItems:"stretch", gap:0, overflowX:"auto" }}>
          {[
            { name:"COORDINATOR", desc:"Orchestrates all agents", color:"var(--accent2)", icon:"⬡", detail:"Controls workflow" },
            { name:"SENTRY",      desc:"Fraud pattern detection", color:"var(--accent)",  icon:"◈", detail:"Gemini AI + Rules" },
            { name:"AUDITOR",     desc:"KYC / AML compliance",   color:"var(--warning)", icon:"◉", detail:"Gemini AI + Watchlist" },
            { name:"RESPONSE",    desc:"Automated mitigation",   color:"var(--danger)",  icon:"⬟", detail:"Auto-action engine" },
          ].map((a,i,arr) => (
            <div key={a.name} style={{ display:"flex", alignItems:"center" }}>
              <div style={{ background:"var(--surface2)", border:`1px solid ${a.color}30`,
                borderTop:`2px solid ${a.color}`, borderRadius:8, padding:"16px 18px",
                textAlign:"center", minWidth:138, flexShrink:0 }}>
                <div style={{ fontSize:20, marginBottom:8 }}>{a.icon}</div>
                <div style={{ fontSize:10, color:a.color, letterSpacing:2, fontWeight:700 }}>{a.name}</div>
                <div style={{ fontSize:9, color:"var(--muted)", marginTop:4 }}>{a.desc}</div>
                <div style={{ fontSize:8, color:a.color, marginTop:6, opacity:0.7, background:`${a.color}12`,
                  padding:"2px 6px", borderRadius:3, letterSpacing:1 }}>{a.detail}</div>
              </div>
              {i<arr.length-1 && <div style={{ fontSize:20, color:"var(--muted)", margin:"0 8px", flexShrink:0 }}>→</div>}
            </div>
          ))}
        </div>
      </div>

      {/* Recent Transactions */}
      <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:10, padding:24 }}>
        <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:16 }}>
          <div style={{ fontSize:10, color:"var(--accent)", letterSpacing:3 }}>RECENT TRANSACTIONS</div>
          <button onClick={()=>onNavigate("transactions")} style={{ background:"none", border:"none",
            color:"var(--muted)", fontSize:10, cursor:"pointer", letterSpacing:2, fontFamily:"inherit" }}>
            VIEW ALL →
          </button>
        </div>
        {txs.length===0 ? (
          <div style={{ color:"var(--muted)", fontSize:11, textAlign:"center", padding:32 }}>
            No transactions yet — click <span style={{color:"var(--accent)"}}>SIMULATE 6 TX</span> to generate demo data.
          </div>
        ) : txs.map(tx => (
          <div key={tx.transaction_id} style={{ display:"flex", alignItems:"center", gap:14,
            padding:"11px 0", borderBottom:"1px solid rgba(255,255,255,0.04)" }}>
            <div style={{ fontSize:16, width:26 }}>{aIcon(tx.action_taken)}</div>
            <div style={{ flex:1, minWidth:0 }}>
              <div style={{ display:"flex", gap:8, alignItems:"center", marginBottom:5 }}>
                <span style={{ fontSize:11, color:"var(--text)", fontWeight:700 }}>#{tx.transaction_id}</span>
                <span style={{ fontSize:9, color:"var(--muted)" }}>{tx.user_id}</span>
                <span style={{ fontSize:9, color:sColor(tx.severity), background:`${sColor(tx.severity)}15`,
                  padding:"2px 6px", borderRadius:3, letterSpacing:1 }}>{tx.severity}</span>
              </div>
              <RiskBar score={tx.fraud_risk_score} />
            </div>
            <div style={{ textAlign:"right", flexShrink:0 }}>
              <div style={{ fontSize:13, color:"var(--text)", fontWeight:700 }}>${tx.amount?.toFixed(2)}</div>
              <div style={{ fontSize:9, color:"var(--muted)" }}>{tx.merchant}</div>
            </div>
            <div style={{ fontSize:12, color:sColor(tx.severity), minWidth:36, textAlign:"right", fontWeight:700 }}>
              {tx.fraud_risk_score}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
