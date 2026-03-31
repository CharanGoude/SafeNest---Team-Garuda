import { useState } from "react";
const API = "http://localhost:8000";

const Field = ({ label, name, value, onChange, type="text", placeholder, options }) => (
  <div style={{ display:"flex", flexDirection:"column", gap:6 }}>
    <label style={{ fontSize:9, color:"var(--muted)", letterSpacing:3 }}>{label}</label>
    {options ? (
      <select name={name} value={value} onChange={onChange} style={{
        background:"var(--surface2)", border:"1px solid var(--border)", borderRadius:6,
        padding:"10px 14px", color:"var(--text)", fontSize:12, fontFamily:"inherit", outline:"none"
      }}>
        {options.map(o=><option key={o} value={o}>{o}</option>)}
      </select>
    ) : (
      <input type={type} name={name} value={value} onChange={onChange} placeholder={placeholder} style={{
        background:"var(--surface2)", border:"1px solid var(--border)", borderRadius:6,
        padding:"10px 14px", color:"var(--text)", fontSize:12, fontFamily:"inherit", outline:"none"
      }}
      onFocus={e=>e.target.style.borderColor="var(--accent)"}
      onBlur={e=>e.target.style.borderColor="var(--border)"} />
    )}
  </div>
);

const AgentStep = ({ log, i }) => {
  const colors = { "Coordinator Agent":"var(--accent2)", "Sentry Agent":"var(--accent)",
    "Auditor Agent":"var(--warning)", "Response Agent":"var(--danger)" };
  const c = colors[log.agent] || "var(--muted)";
  return (
    <div style={{ display:"flex", gap:14, animation:`fadeUp 0.3s ease ${i*0.1}s both` }}>
      <div style={{ display:"flex", flexDirection:"column", alignItems:"center", width:32, flexShrink:0 }}>
        <div style={{ width:28, height:28, borderRadius:"50%", background:`${c}15`, border:`1px solid ${c}`,
          display:"flex", alignItems:"center", justifyContent:"center", fontSize:11, color:c, fontWeight:700 }}>
          {i+1}
        </div>
        {<div style={{ width:1, flex:1, background:"var(--border)", margin:"6px 0", minHeight:12 }} />}
      </div>
      <div style={{ flex:1, paddingBottom:16 }}>
        <div style={{ fontSize:9, color:c, letterSpacing:2, marginBottom:2 }}>{log.agent.toUpperCase()}</div>
        <div style={{ fontSize:12, color:"var(--text)", fontWeight:700, marginBottom:3 }}>{log.result_summary || log.agent}</div>
        <div style={{ fontSize:10, color:"var(--muted)" }}>Processed in {log.duration_ms}ms</div>
      </div>
    </div>
  );
};

export default function AnalyzePage() {
  const [form, setForm] = useState({
    user_id:"user_123", account_number:"ACC001TEST", amount:"2500",
    currency:"USD", transaction_type:"PAYMENT",
    merchant_name:"Amazon", merchant_category:"RETAIL",
    location_country:"IN", location_city:"Mumbai",
    device_id:"iPhone_14", ip_address:"192.168.1.1",
    is_new_device:"false", previous_transaction_minutes_ago:"60",
    user_avg_transaction:"800", account_age_days:"365"
  });
  const [result, setResult]   = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]     = useState(null);

  const onChange = e => setForm({...form, [e.target.name]: e.target.value});

  const analyze = async () => {
    setLoading(true); setError(null); setResult(null);
    try {
      const r = await fetch(`${API}/analyze`, {
        method:"POST", headers:{"Content-Type":"application/json"},
        body: JSON.stringify({
          ...form,
          amount: parseFloat(form.amount),
          is_new_device: form.is_new_device === "true",
          previous_transaction_minutes_ago: form.previous_transaction_minutes_ago ? parseInt(form.previous_transaction_minutes_ago) : null,
          user_avg_transaction: parseFloat(form.user_avg_transaction),
          account_age_days: parseInt(form.account_age_days),
        })
      });
      setResult(await r.json());
    } catch { setError("Cannot connect to backend. Start FastAPI on port 8000."); }
    setLoading(false);
  };

  const score    = result?.fraud_risk_score || 0;
  const severity = result?.severity;
  const action   = result?.action_taken;
  const sColor   = s => ({CRITICAL:"var(--danger)",WARNING:"var(--warning)",INFO:"var(--accent)"}[s]||"var(--muted)");
  const rc       = sColor(severity);

  return (
    <div>
      <div style={{ marginBottom:32 }}>
        <div style={{ fontSize:10, color:"var(--accent)", letterSpacing:4, marginBottom:4 }}>AGENT ANALYSIS</div>
        <h1 style={{ fontSize:28, fontWeight:800, fontFamily:"'Syne',sans-serif" }}>Analyze Transaction</h1>
        <p style={{ fontSize:11, color:"var(--muted)", marginTop:4 }}>Submit a transaction through all 4 AI agents in real-time</p>
      </div>

      <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:24, alignItems:"start" }}>
        {/* Input Form */}
        <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:10, padding:28 }}>
          <div style={{ fontSize:10, color:"var(--accent)", letterSpacing:3, marginBottom:20 }}>TRANSACTION DETAILS</div>
          <div style={{ display:"grid", gridTemplateColumns:"1fr 1fr", gap:14 }}>
            <Field label="USER ID"          name="user_id"           value={form.user_id}           onChange={onChange} />
            <Field label="ACCOUNT NUMBER"   name="account_number"    value={form.account_number}    onChange={onChange} placeholder="ACC001TEST" />
            <Field label="AMOUNT (USD)"     name="amount"            value={form.amount}            onChange={onChange} type="number" />
            <Field label="TX TYPE"          name="transaction_type"  value={form.transaction_type}  onChange={onChange}
              options={["PAYMENT","TRANSFER","WITHDRAWAL","DEPOSIT"]} />
            <Field label="MERCHANT NAME"    name="merchant_name"     value={form.merchant_name}     onChange={onChange} />
            <Field label="MERCHANT CATEGORY" name="merchant_category" value={form.merchant_category} onChange={onChange}
              options={["RETAIL","STREAMING","CRYPTO","FOOD","TRANSFER","RIDE_SHARE","GAMING"]} />
            <Field label="COUNTRY"          name="location_country"  value={form.location_country}  onChange={onChange} />
            <Field label="CITY"             name="location_city"     value={form.location_city}     onChange={onChange} />
            <Field label="DEVICE ID"        name="device_id"         value={form.device_id}         onChange={onChange} />
            <Field label="IP ADDRESS"       name="ip_address"        value={form.ip_address}        onChange={onChange} />
            <Field label="NEW DEVICE?"      name="is_new_device"     value={form.is_new_device}     onChange={onChange}
              options={["false","true"]} />
            <Field label="MINS SINCE LAST TX" name="previous_transaction_minutes_ago" value={form.previous_transaction_minutes_ago} onChange={onChange} type="number" />
            <Field label="USER AVG TX ($)"  name="user_avg_transaction" value={form.user_avg_transaction} onChange={onChange} type="number" />
            <Field label="ACCOUNT AGE (DAYS)" name="account_age_days" value={form.account_age_days} onChange={onChange} type="number" />
          </div>

          {/* Try high-risk presets */}
          <div style={{ marginTop:16, display:"flex", gap:8, flexWrap:"wrap" }}>
            <div style={{ fontSize:9, color:"var(--muted)", letterSpacing:2, width:"100%", marginBottom:4 }}>QUICK PRESETS:</div>
            {[
              { label:"🟢 Safe TX",    vals:{ amount:"150", merchant_name:"Starbucks", location_country:"IN", account_age_days:"365", is_new_device:"false", user_avg_transaction:"200" }},
              { label:"🟡 Suspicious", vals:{ amount:"9500", merchant_name:"QuickCash", location_country:"RU", account_age_days:"15",  is_new_device:"true",  user_avg_transaction:"300" }},
              { label:"🔴 High Risk",  vals:{ account_number:"ACC999BLACKLIST", amount:"15000", merchant_name:"CryptoFast", location_country:"KP", is_new_device:"true", previous_transaction_minutes_ago:"1" }},
            ].map(p => (
              <button key={p.label} onClick={()=>setForm({...form,...p.vals})} style={{
                background:"rgba(255,255,255,0.04)", border:"1px solid var(--border)", borderRadius:5,
                color:"var(--muted)", padding:"5px 10px", cursor:"pointer", fontSize:10, fontFamily:"inherit"
              }}>{p.label}</button>
            ))}
          </div>

          <button onClick={analyze} disabled={loading} style={{
            width:"100%", marginTop:20, padding:"13px", background:"rgba(0,255,136,0.1)",
            border:"1px solid var(--accent)", borderRadius:7, color:"var(--accent)", cursor:loading?"default":"pointer",
            fontSize:12, letterSpacing:3, fontFamily:"inherit", fontWeight:700
          }}>
            {loading ? "⟳ AGENTS PROCESSING..." : "▶ RUN THROUGH ALL 4 AGENTS"}
          </button>
          {error && <div style={{ marginTop:10, fontSize:11, color:"var(--danger)" }}>{error}</div>}
        </div>

        {/* Result Panel */}
        <div style={{ display:"flex", flexDirection:"column", gap:16 }}>
          {result ? (<>
            {/* Risk Gauge */}
            <div style={{ background:"var(--surface)", border:`1px solid ${rc}40`, borderRadius:10, padding:24 }}>
              <div style={{ fontSize:10, color:"var(--accent)", letterSpacing:3, marginBottom:16 }}>RISK ASSESSMENT</div>
              <div style={{ display:"flex", gap:20, alignItems:"center" }}>
                <div style={{ width:88, height:88, borderRadius:"50%", border:`3px solid ${rc}`,
                  display:"flex", flexDirection:"column", alignItems:"center", justifyContent:"center",
                  boxShadow:`0 0 28px ${rc}40`, background:`${rc}10`, flexShrink:0 }}>
                  <span style={{ fontSize:26, fontWeight:800, color:rc, fontFamily:"'Syne',sans-serif", lineHeight:1 }}>{score}</span>
                  <span style={{ fontSize:8, color:rc, opacity:0.7, letterSpacing:1 }}>/100</span>
                </div>
                <div>
                  <div style={{ fontSize:13, color:"var(--text)", fontWeight:700, marginBottom:4 }}>
                    {action?.replace(/_/g," ")}
                  </div>
                  <div style={{ fontSize:10, color:"var(--muted)", marginBottom:8, lineHeight:1.6 }}>
                    {result.response?.alert_message || result.response?.reasoning?.slice(0,120)}
                  </div>
                  <div style={{ display:"flex", gap:8 }}>
                    <span style={{ fontSize:9, color:rc, background:`${rc}18`, padding:"3px 10px", borderRadius:3, letterSpacing:2 }}>{severity}</span>
                    <span style={{ fontSize:9, color:"var(--muted)", background:"rgba(255,255,255,0.05)", padding:"3px 10px", borderRadius:3, letterSpacing:1 }}>
                      {result.risk_level}
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Fraud Indicators */}
            {result.sentry?.fraud_indicators?.length > 0 && (
              <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:10, padding:20 }}>
                <div style={{ fontSize:10, color:"var(--warning)", letterSpacing:3, marginBottom:12 }}>
                  FRAUD INDICATORS ({result.sentry.fraud_indicators.length})
                </div>
                {result.sentry.fraud_indicators.map((f,i)=>(
                  <div key={i} style={{ display:"flex", gap:8, fontSize:11, color:"var(--text)",
                    padding:"6px 0", borderBottom:"1px solid rgba(255,255,255,0.04)" }}>
                    <span style={{color:"var(--warning)"}}>⚠</span>{f}
                  </div>
                ))}
                {result.sentry.behavioural_analysis && (
                  <div style={{ fontSize:10, color:"var(--muted)", marginTop:10, padding:"10px 12px",
                    background:"rgba(255,255,255,0.03)", borderRadius:6, lineHeight:1.7 }}>
                    {result.sentry.behavioural_analysis}
                  </div>
                )}
              </div>
            )}

            {/* Compliance */}
            <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:10, padding:20 }}>
              <div style={{ fontSize:10, color:"var(--accent2)", letterSpacing:3, marginBottom:12 }}>COMPLIANCE CHECKS</div>
              {[
                { k:"KYC",       v: result.auditor?.kyc_status },
                { k:"AML",       v: result.auditor?.aml_status },
                { k:"WATCHLIST", v: result.auditor?.watchlist_status },
                { k:"CTR REQ",   v: result.auditor?.ctr_required ? "YES" : "NO" },
                { k:"STATUS",    v: result.auditor?.compliance_status },
              ].map(({k,v}) => {
                const cc = ["VERIFIED","CLEAR","NO","COMPLIANT"].includes(v)?"var(--accent)":
                           ["FAILED","VIOLATION","MATCH_FOUND","NON_COMPLIANT"].includes(v)?"var(--danger)":"var(--warning)";
                return (
                  <div key={k} style={{ display:"flex", justifyContent:"space-between", padding:"8px 0",
                    borderBottom:"1px solid rgba(255,255,255,0.04)", fontSize:11 }}>
                    <span style={{ color:"var(--muted)" }}>{k}</span>
                    <span style={{ color:cc, fontWeight:700 }}>{v||"—"}</span>
                  </div>
                );
              })}
              {result.auditor?.regulatory_flags?.length > 0 && (
                <div style={{ marginTop:10 }}>
                  {result.auditor.regulatory_flags.map((f,i)=>(
                    <div key={i} style={{ fontSize:10, color:"var(--warning)", marginTop:4 }}>⚑ {f}</div>
                  ))}
                </div>
              )}
            </div>

            {/* Secondary Actions */}
            {result.response?.secondary_actions?.length > 0 && (
              <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:10, padding:20 }}>
                <div style={{ fontSize:10, color:"var(--danger)", letterSpacing:3, marginBottom:10 }}>SECONDARY ACTIONS</div>
                <div style={{ display:"flex", gap:8, flexWrap:"wrap" }}>
                  {result.response.secondary_actions.map(a=>(
                    <span key={a} style={{ fontSize:9, color:"var(--danger)", background:"rgba(255,59,59,0.1)",
                      padding:"4px 10px", borderRadius:3, letterSpacing:1 }}>{a.replace(/_/g," ")}</span>
                  ))}
                </div>
              </div>
            )}
          </>) : (
            <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:10, padding:40,
              textAlign:"center", color:"var(--muted)", fontSize:11, lineHeight:2 }}>
              Use presets or fill in transaction data,<br/>then click <span style={{color:"var(--accent)"}}>▶ RUN THROUGH ALL 4 AGENTS</span>
            </div>
          )}
        </div>
      </div>

      {/* Agent Pipeline Trace */}
      {result?.agent_pipeline && (
        <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:10, padding:24, marginTop:24 }}>
          <div style={{ display:"flex", justifyContent:"space-between", alignItems:"center", marginBottom:20 }}>
            <div style={{ fontSize:10, color:"var(--accent)", letterSpacing:3 }}>AGENT EXECUTION TRACE</div>
            <div style={{ fontSize:10, color:"var(--muted)" }}>Total: {result.total_processing_ms}ms</div>
          </div>
          {result.agent_pipeline.map((log,i) => <AgentStep key={i} log={log} i={i} />)}
          {result.coordinator?.key_findings?.length > 0 && (
            <div style={{ marginTop:12, padding:"12px 16px", background:"rgba(0,255,136,0.04)",
              border:"1px solid rgba(0,255,136,0.12)", borderRadius:8 }}>
              <div style={{ fontSize:9, color:"var(--accent)", letterSpacing:2, marginBottom:8 }}>COORDINATOR SUMMARY</div>
              <div style={{ fontSize:11, color:"var(--muted)" }}>{result.coordinator.summary}</div>
              {result.coordinator.key_findings.map((f,i)=>(
                <div key={i} style={{ fontSize:10, color:"var(--text)", marginTop:5 }}>• {f}</div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
}
