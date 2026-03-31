import { useState, useEffect } from "react";
const API = "http://localhost:8000";

const sColor = s => ({CRITICAL:"var(--danger)",WARNING:"var(--warning)",INFO:"var(--accent)"}[s]||"var(--muted)");
const aIcon  = a => ({BLOCK:"🔒",FREEZE_ACCOUNT:"🔒",REQUIRE_OTP:"📱",REQUIRE_BIOMETRIC:"🔐",FLAG_FOR_REVIEW:"⚑",APPROVE:"✓"}[a]||"?");

export default function TransactionsPage() {
  const [txs, setTxs]         = useState([]);
  const [filter, setFilter]   = useState("ALL");
  const [selected, setSelected] = useState(null);

  useEffect(() => {
    const go = async () => {
      try { const r = await fetch(`${API}/transactions?limit=100`).then(r=>r.json()); setTxs(r.transactions||[]); } catch{}
    };
    go(); const id = setInterval(go, 4000); return ()=>clearInterval(id);
  }, []);

  const FILTERS = ["ALL","CRITICAL","WARNING","INFO"];
  const filtered = filter==="ALL" ? txs : txs.filter(t=>t.severity===filter);

  return (
    <div>
      <div style={{ marginBottom:28 }}>
        <div style={{ fontSize:10, color:"var(--accent)", letterSpacing:4, marginBottom:4 }}>TRANSACTION LOG</div>
        <h1 style={{ fontSize:28, fontWeight:800, fontFamily:"'Syne',sans-serif" }}>All Transactions</h1>
        <p style={{ fontSize:11, color:"var(--muted)", marginTop:4 }}>{txs.length} transactions recorded</p>
      </div>

      <div style={{ display:"flex", gap:8, marginBottom:20 }}>
        {FILTERS.map(f=>(
          <button key={f} onClick={()=>setFilter(f)} style={{
            padding:"7px 16px", border:`1px solid ${filter===f?sColor(f):"var(--border)"}`,
            background:filter===f?`${sColor(f)}10`:"transparent",
            color:filter===f?sColor(f):"var(--muted)",
            borderRadius:6, cursor:"pointer", fontFamily:"inherit", fontSize:10, letterSpacing:2
          }}>{f}</button>
        ))}
        <div style={{ marginLeft:"auto", fontSize:11, color:"var(--muted)", display:"flex", alignItems:"center" }}>
          {filtered.length} shown
        </div>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:selected?"1fr 1fr":"1fr", gap:20 }}>
        {/* Table */}
        <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:10, overflow:"hidden" }}>
          <div style={{ display:"grid", gridTemplateColumns:"90px 90px 1fr 110px 70px 120px 80px",
            padding:"11px 18px", fontSize:9, color:"var(--muted)", letterSpacing:2,
            borderBottom:"1px solid var(--border)", gap:10 }}>
            <span>TX ID</span><span>USER</span><span>MERCHANT</span><span>AMOUNT</span><span>RISK</span><span>ACTION</span><span>SEV</span>
          </div>
          {filtered.length===0 ? (
            <div style={{ padding:40, textAlign:"center", color:"var(--muted)", fontSize:11 }}>No transactions found.</div>
          ) : filtered.map(tx=>(
            <div key={tx.transaction_id} onClick={()=>setSelected(tx===selected?null:tx)} style={{
              display:"grid", gridTemplateColumns:"90px 90px 1fr 110px 70px 120px 80px",
              padding:"11px 18px", cursor:"pointer", gap:10, fontSize:11,
              background:selected?.transaction_id===tx.transaction_id?"rgba(0,255,136,0.04)":"transparent",
              borderBottom:"1px solid rgba(255,255,255,0.03)",
              borderLeft:selected?.transaction_id===tx.transaction_id?"2px solid var(--accent)":"2px solid transparent",
              transition:"background 0.15s"
            }}>
              <span style={{ color:"var(--accent2)", fontWeight:700 }}>#{tx.transaction_id}</span>
              <span style={{ color:"var(--muted)" }}>{tx.user_id}</span>
              <span style={{ color:"var(--text)", overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>{tx.merchant}</span>
              <span style={{ color:"var(--text)", fontWeight:700 }}>${tx.amount?.toFixed(2)}</span>
              <span style={{ color:sColor(tx.severity), fontWeight:700 }}>{tx.fraud_risk_score}</span>
              <span style={{ fontSize:9, color:sColor(tx.severity), overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                {aIcon(tx.action_taken)} {tx.action_taken?.replace(/_/g," ")}
              </span>
              <span style={{ fontSize:9, color:sColor(tx.severity), background:`${sColor(tx.severity)}15`,
                padding:"2px 6px", borderRadius:3, letterSpacing:1, textAlign:"center" }}>{tx.severity}</span>
            </div>
          ))}
        </div>

        {/* Detail Panel */}
        {selected && (
          <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:10, padding:24, animation:"slideIn 0.2s ease", overflowY:"auto", maxHeight:"80vh" }}>
            <div style={{ display:"flex", justifyContent:"space-between", marginBottom:20 }}>
              <div style={{ fontSize:10, color:"var(--accent)", letterSpacing:3 }}>TX DETAIL</div>
              <button onClick={()=>setSelected(null)} style={{ background:"none", border:"none", color:"var(--muted)", cursor:"pointer", fontSize:16 }}>✕</button>
            </div>

            <div style={{ fontSize:22, fontWeight:800, fontFamily:"'Syne',sans-serif", color:"var(--accent2)", marginBottom:2 }}>#{selected.transaction_id}</div>
            <div style={{ fontSize:32, fontWeight:800, fontFamily:"'Syne',sans-serif", marginBottom:4 }}>${selected.amount?.toFixed(2)}</div>
            <div style={{ fontSize:10, color:"var(--muted)", marginBottom:20, letterSpacing:1 }}>{selected.currency} · {selected.timestamp?.slice(0,19).replace("T"," ")} UTC</div>

            {[["User",selected.user_id],["Account",selected.account_number],["Merchant",selected.merchant],
              ["Location",selected.location],["Risk Level",selected.risk_level],
              ["Compliance",selected.compliance_status]].map(([k,v])=>(
              <div key={k} style={{ display:"flex", justifyContent:"space-between", padding:"7px 0",
                borderBottom:"1px solid rgba(255,255,255,0.04)", fontSize:11 }}>
                <span style={{ color:"var(--muted)" }}>{k}</span>
                <span style={{ color:"var(--text)" }}>{v||"—"}</span>
              </div>
            ))}

            <div style={{ marginTop:16, padding:"12px 14px", background:`${sColor(selected.severity)}08`,
              border:`1px solid ${sColor(selected.severity)}25`, borderRadius:8 }}>
              <div style={{ fontSize:9, color:sColor(selected.severity), letterSpacing:2, marginBottom:4 }}>ACTION TAKEN</div>
              <div style={{ fontSize:12, color:"var(--text)", fontWeight:700 }}>{selected.action_taken?.replace(/_/g," ")}</div>
              {selected.response?.secondary_actions?.length > 0 && (
                <div style={{ marginTop:8, display:"flex", gap:6, flexWrap:"wrap" }}>
                  {selected.response.secondary_actions.map(a=>(
                    <span key={a} style={{ fontSize:9, color:sColor(selected.severity), background:`${sColor(selected.severity)}15`,
                      padding:"2px 8px", borderRadius:3 }}>{a.replace(/_/g," ")}</span>
                  ))}
                </div>
              )}
            </div>

            {selected.sentry?.fraud_indicators?.length > 0 && (
              <div style={{ marginTop:16 }}>
                <div style={{ fontSize:9, color:"var(--warning)", letterSpacing:2, marginBottom:8 }}>FRAUD FLAGS</div>
                {selected.sentry.fraud_indicators.map((f,i)=>(
                  <div key={i} style={{ fontSize:10, color:"var(--muted)", padding:"3px 0", display:"flex", gap:8 }}>
                    <span style={{ color:"var(--warning)" }}>⚠</span>{f}
                  </div>
                ))}
              </div>
            )}

            {/* Processing time */}
            {selected.agent_pipeline?.length > 0 && (
              <div style={{ marginTop:16 }}>
                <div style={{ fontSize:9, color:"var(--accent)", letterSpacing:2, marginBottom:8 }}>PROCESSING TIME</div>
                {selected.agent_pipeline.map((s,i)=>(
                  <div key={i} style={{ display:"flex", justifyContent:"space-between", fontSize:10, padding:"4px 0",
                    borderBottom:"1px solid rgba(255,255,255,0.03)", color:"var(--muted)" }}>
                    <span>{s.agent}</span>
                    <span style={{ color:"var(--text)" }}>{s.duration_ms}ms</span>
                  </div>
                ))}
                <div style={{ display:"flex", justifyContent:"space-between", fontSize:10, padding:"6px 0",
                  color:"var(--accent)", fontWeight:700, marginTop:2 }}>
                  <span>TOTAL</span>
                  <span>{selected.total_processing_ms}ms</span>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
