import { useState, useEffect } from "react";
import api from "../utils/api";
import { RiskBadge, ActionBadge, RiskBar, Card, Button, EmptyState, Spinner } from "../components/UI";

const FILTERS = ["ALL", "CRITICAL", "HIGH", "MEDIUM", "LOW"];

export default function TransactionsPage() {
  const [txs, setTxs]         = useState([]);
  const [filter, setFilter]   = useState("ALL");
  const [selected, setSelected] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetch_ = async () => {
      try {
        const r = await api.transactions({ limit: 100 });
        setTxs(r.transactions || []);
      } catch {}
      finally { setLoading(false); }
    };
    fetch_();
    const id = setInterval(fetch_, 6000);
    return () => clearInterval(id);
  }, []);

  const filtered = filter === "ALL" ? txs : txs.filter(t => t.risk_level === filter);

  const fColor = f => ({
    CRITICAL:"#dc2626", HIGH:"#ea580c", MEDIUM:"#d97706", LOW:"#16a34a", ALL:"#2563eb"
  }[f] || "#94a3b8");

  if (loading) return (
    <div style={{ display:"flex", alignItems:"center", justifyContent:"center", height:300, gap:12, color:"#94a3b8" }}>
      <Spinner size={22} /> Loading transactions...
    </div>
  );

  return (
    <div style={{ animation:"fadeUp 0.3s ease" }}>
      <div style={{ marginBottom:24 }}>
        <h1 style={{ fontSize:22, fontWeight:800, color:"#0f172a", marginBottom:4 }}>Transactions</h1>
        <p style={{ fontSize:13, color:"#94a3b8" }}>{txs.length} total · updates every 6 seconds</p>
      </div>

      {/* Filters */}
      <div style={{ display:"flex", gap:8, marginBottom:16, flexWrap:"wrap", alignItems:"center" }}>
        {FILTERS.map(f => (
          <button key={f} onClick={() => setFilter(f)} style={{
            padding:"6px 14px", border:`1px solid ${filter===f ? fColor(f) : "#e2e8f0"}`,
            background: filter===f ? `${fColor(f)}12` : "#fff",
            color: filter===f ? fColor(f) : "#64748b",
            borderRadius:8, cursor:"pointer", fontFamily:"inherit",
            fontSize:12, fontWeight:600, transition:"all 0.15s"
          }}>{f}</button>
        ))}
        <span style={{ marginLeft:"auto", fontSize:12, color:"#94a3b8" }}>
          {filtered.length} shown
        </span>
      </div>

      <div style={{ display:"grid", gridTemplateColumns: selected ? "1fr 1fr" : "1fr", gap:16 }}>
        {/* Table */}
        <Card>
          {/* Table Header */}
          <div style={{
            display:"grid", gridTemplateColumns:"90px 100px 1fr 100px 60px 140px 90px",
            padding:"10px 16px", background:"#f8fafc",
            borderBottom:"1px solid #e2e8f0", gap:8
          }}>
            {["TX ID","USER","MERCHANT","AMOUNT","SCORE","ACTION","RISK"].map(h => (
              <div key={h} style={{ fontSize:10, fontWeight:700, color:"#94a3b8", textTransform:"uppercase", letterSpacing:0.5 }}>{h}</div>
            ))}
          </div>

          {filtered.length === 0 ? (
            <EmptyState icon="📭" title="No transactions" subtitle="Adjust filter or simulate transactions" />
          ) : filtered.map((tx, i) => (
            <div key={tx.transaction_id}
              onClick={() => setSelected(tx === selected ? null : tx)}
              style={{
                display:"grid", gridTemplateColumns:"90px 100px 1fr 100px 60px 140px 90px",
                padding:"11px 16px", gap:8, cursor:"pointer",
                background: selected?.transaction_id === tx.transaction_id ? "#eff6ff" : i%2===0 ? "#fff" : "#fafafa",
                borderBottom:"1px solid #f1f5f9",
                borderLeft: selected?.transaction_id === tx.transaction_id ? "3px solid #2563eb" : "3px solid transparent",
                transition:"background 0.1s"
              }}>
              <div style={{ fontSize:11, fontWeight:700, color:"#2563eb", fontFamily:"monospace", overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                #{tx.transaction_id}
              </div>
              <div style={{ fontSize:11, color:"#64748b", overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                {tx.user_id}
              </div>
              <div style={{ fontSize:12, color:"#0f172a", overflow:"hidden", textOverflow:"ellipsis", whiteSpace:"nowrap" }}>
                {tx.merchant_name}
              </div>
              <div style={{ fontSize:12, fontWeight:700, color:"#0f172a" }}>
                ${tx.amount?.toFixed(2)}
              </div>
              <div style={{ fontSize:12, fontWeight:800, color: tx.final_risk_score>=75?"#dc2626":tx.final_risk_score>=50?"#ea580c":tx.final_risk_score>=30?"#d97706":"#16a34a" }}>
                {tx.final_risk_score}
              </div>
              <div><ActionBadge action={tx.action} /></div>
              <div><RiskBadge level={tx.risk_level} /></div>
            </div>
          ))}
        </Card>

        {/* Detail Panel */}
        {selected && (
          <Card style={{ animation:"slideIn 0.2s ease", maxHeight:"80vh", overflowY:"auto" }}>
            <div style={{ padding:"16px 20px" }}>
              <div style={{ display:"flex", justifyContent:"space-between", marginBottom:16 }}>
                <div style={{ fontSize:13, fontWeight:700, color:"#0f172a" }}>Transaction Detail</div>
                <button onClick={() => setSelected(null)} style={{ background:"none", border:"none", cursor:"pointer", fontSize:18, color:"#94a3b8" }}>✕</button>
              </div>

              <div style={{ fontFamily:"monospace", fontSize:18, fontWeight:800, color:"#2563eb", marginBottom:2 }}>
                #{selected.transaction_id}
              </div>
              <div style={{ fontSize:30, fontWeight:800, color:"#0f172a", marginBottom:4 }}>
                ${selected.amount?.toFixed(2)}
              </div>
              <div style={{ fontSize:11, color:"#94a3b8", marginBottom:16 }}>
                {selected.currency} · {selected.timestamp?.slice(0,19).replace("T"," ")} UTC
              </div>

              <div style={{ marginBottom:16 }}>
                <RiskBar score={selected.final_risk_score} showLabel />
              </div>

              <div style={{ marginBottom:16 }}>
                <ActionBadge action={selected.action} />
                <span style={{ marginLeft:8 }}><RiskBadge level={selected.risk_level} /></span>
              </div>

              {[
                ["User",       selected.user_id],
                ["Account",    selected.account_number],
                ["Merchant",   selected.merchant_name],
                ["Category",   selected.merchant_category],
                ["Country",    selected.location_country],
                ["City",       selected.location_city],
                ["Device",     selected.device_id],
                ["IP Address", selected.ip_address],
                ["New Device", selected.is_new_device ? "Yes" : "No"],
                ["Compliance", selected.compliance_status],
                ["CTR Filed",  selected.ctr_required ? "Yes" : "No"],
                ["SAR Filed",  selected.sar_required ? "Yes" : "No"],
                ["Sentry Score", selected.sentry_score],
                ["Processing",  `${selected.processing_time_ms}ms`],
              ].map(([k,v]) => v !== undefined && v !== null && (
                <div key={k} style={{ display:"flex", justifyContent:"space-between", padding:"6px 0", borderBottom:"1px solid #f8fafc", fontSize:12 }}>
                  <span style={{ color:"#64748b" }}>{k}</span>
                  <span style={{ color:"#0f172a", fontWeight:500, textAlign:"right", maxWidth:"60%", wordBreak:"break-all" }}>{v}</span>
                </div>
              ))}

              {selected.fraud_indicators?.length > 0 && (
                <div style={{ marginTop:14 }}>
                  <div style={{ fontSize:11, fontWeight:700, color:"#d97706", letterSpacing:0.5, textTransform:"uppercase", marginBottom:6 }}>
                    Fraud Indicators
                  </div>
                  {selected.fraud_indicators.map((f,i) => (
                    <div key={i} style={{ fontSize:11, color:"#475569", padding:"3px 0", display:"flex", gap:6 }}>
                      <span style={{ color:"#d97706" }}>⚠</span>{f}
                    </div>
                  ))}
                </div>
              )}

              {selected.regulatory_flags?.length > 0 && (
                <div style={{ marginTop:14 }}>
                  <div style={{ fontSize:11, fontWeight:700, color:"#dc2626", letterSpacing:0.5, textTransform:"uppercase", marginBottom:6 }}>
                    Regulatory Flags
                  </div>
                  {selected.regulatory_flags.map((f,i) => (
                    <div key={i} style={{ fontSize:11, color:"#475569", padding:"3px 0", display:"flex", gap:6 }}>
                      <span style={{ color:"#dc2626" }}>⚑</span>{f}
                    </div>
                  ))}
                </div>
              )}
            </div>
          </Card>
        )}
      </div>
    </div>
  );
}
