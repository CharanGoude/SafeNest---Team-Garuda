import { useState } from "react";
import api from "../utils/api";
import { RiskBadge, ActionBadge, RiskBar, Card, Button, Spinner } from "../components/UI";

const PRESETS = {
  safe: {
    label: "🟢 Safe Transaction",
    data: { user_id:"user_rahul_k", account_number:"ACC101RAHUL", amount:12500, currency:"INR", transaction_type:"PAYMENT", merchant_name:"Amazon India", merchant_category:"RETAIL", location_country:"IN", location_city:"Mumbai", device_id:"iPhone_14_A1", ip_address:"192.168.1.100", is_new_device:false, account_age_days:730, user_avg_transaction:12500, previous_transaction_minutes_ago:120 }
  },
  medium: {
    label: "🟡 Suspicious",
    data: { user_id:"user_priya_m", account_number:"ACC102PRIYA", amount:375000, currency:"INR", transaction_type:"TRANSFER", merchant_name:"CryptoSwap", merchant_category:"CRYPTO", location_country:"RU", location_city:"Moscow", device_id:"UNKNOWN_DEVICE_X7", ip_address:"91.108.45.22", is_new_device:true, account_age_days:365, user_avg_transaction:66400, previous_transaction_minutes_ago:8 }
  },
  high: {
    label: "🔴 High Risk",
    data: { user_id:"user_test", account_number:"ACC103TEST", amount:996000, currency:"INR", transaction_type:"WITHDRAWAL", merchant_name:"QuickCash247", merchant_category:"TRANSFER", location_country:"KP", location_city:"Unknown", device_id:"UNKNOWN_DEVICE_99", ip_address:"185.220.101.45", is_new_device:true, account_age_days:15, user_avg_transaction:24900, previous_transaction_minutes_ago:1 }
  },
  critical: {
    label: "🚨 Blacklisted",
    data: { user_id:"user_blacklist", account_number:"ACC999BLACKLIST", amount:1245000, currency:"INR", transaction_type:"TRANSFER", merchant_name:"AnonPay", merchant_category:"TRANSFER", location_country:"IR", location_city:"Unknown", device_id:"UNKNOWN_DEVICE_CRITICAL", ip_address:"185.220.101.99", is_new_device:true, account_age_days:200, user_avg_transaction:41500, previous_transaction_minutes_ago:1 }
  }
};

const FORM_FIELDS = [
  { key:"user_id",           label:"User ID",            type:"text",   placeholder:"user_rahul_k" },
  { key:"account_number",    label:"Account Number",     type:"text",   placeholder:"ACC123456789" },
  { key:"amount",            label:"Amount (USD)",       type:"number", placeholder:"1000" },
  { key:"merchant_name",     label:"Merchant Name",      type:"text",   placeholder:"Amazon India" },
  { key:"location_country",  label:"Country Code",       type:"text",   placeholder:"IN" },
  { key:"location_city",     label:"City",               type:"text",   placeholder:"Mumbai" },
  { key:"device_id",         label:"Device ID",          type:"text",   placeholder:"iPhone_14_A1" },
  { key:"ip_address",        label:"IP Address",         type:"text",   placeholder:"192.168.1.1" },
  { key:"account_age_days",  label:"Account Age (days)", type:"number", placeholder:"365" },
  { key:"user_avg_transaction", label:"Avg Transaction ($)", type:"number", placeholder:"500" },
  { key:"previous_transaction_minutes_ago", label:"Mins Since Last TX", type:"number", placeholder:"60" },
];

const SELECT_FIELDS = [
  { key:"transaction_type",  label:"Transaction Type",  options:["PAYMENT","TRANSFER","WITHDRAWAL","DEPOSIT"] },
  { key:"merchant_category", label:"Merchant Category", options:["RETAIL","FOOD","STREAMING","CRYPTO","TRANSFER","GAMING","RIDE_SHARE"] },
  { key:"currency",          label:"Currency",          options:["USD","INR","EUR","GBP","AED"] },
];

const inputStyle = {
  width: "100%", padding: "9px 12px", border: "1px solid #e2e8f0",
  borderRadius: 8, fontSize: 13, fontFamily: "inherit",
  background: "#f8fafc", color: "#0f172a", outline: "none",
  transition: "border-color 0.15s"
};

export default function AnalyzePage() {
  const [form, setForm]     = useState({ ...PRESETS.safe.data });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError]   = useState(null);

  const onChange = e => {
    const val = e.target.type === "checkbox" ? e.target.checked
              : e.target.type === "number"   ? parseFloat(e.target.value) || 0
              : e.target.value;
    setForm({ ...form, [e.target.name]: val });
  };

  const applyPreset = (key) => {
    setForm({ ...PRESETS[key].data });
    setResult(null);
    setError(null);
  };

  const analyze = async () => {
    setLoading(true); setError(null); setResult(null);
    try {
      const res = await api.analyze(form);
      setResult(res);
    } catch (e) {
      setError(e.message || "Analysis failed. Check backend connection.");
    }
    setLoading(false);
  };

  const score     = result?.final_risk_score ?? 0;
  const action    = result?.action;
  const riskLevel = result?.risk_level;
  const scoreColor = score >= 75 ? "#dc2626" : score >= 50 ? "#ea580c" : score >= 30 ? "#d97706" : "#16a34a";

  return (
    <div style={{ animation: "fadeUp 0.3s ease" }}>
      <div style={{ marginBottom: 24 }}>
        <h1 style={{ fontSize: 22, fontWeight: 800, color: "#0f172a", marginBottom: 4 }}>
          Analyze Transaction
        </h1>
        <p style={{ fontSize: 13, color: "#94a3b8" }}>
          Submit a transaction through all 3 agents · Real-time analysis
        </p>
      </div>

      {/* Presets */}
      <div style={{ display: "flex", gap: 8, marginBottom: 20, flexWrap: "wrap" }}>
        <span style={{ fontSize: 12, color: "#94a3b8", alignSelf: "center", marginRight: 4 }}>Quick presets:</span>
        {Object.entries(PRESETS).map(([key, p]) => (
          <Button key={key} variant="secondary" size="sm" onClick={() => applyPreset(key)}>
            {p.label}
          </Button>
        ))}
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20, alignItems: "start" }}>
        {/* Form */}
        <Card title="Transaction Details" style={{}}>
          <div style={{ padding: "16px 20px" }}>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
              {FORM_FIELDS.map(f => (
                <div key={f.key}>
                  <label style={{ fontSize: 11, color: "#64748b", fontWeight: 600, display: "block", marginBottom: 4, textTransform: "uppercase", letterSpacing: 0.5 }}>
                    {f.label}
                  </label>
                  <input
                    type={f.type} name={f.key} value={form[f.key] || ""}
                    onChange={onChange} placeholder={f.placeholder}
                    style={inputStyle}
                    onFocus={e => e.target.style.borderColor="#2563eb"}
                    onBlur={e => e.target.style.borderColor="#e2e8f0"}
                  />
                </div>
              ))}
              {SELECT_FIELDS.map(f => (
                <div key={f.key}>
                  <label style={{ fontSize: 11, color: "#64748b", fontWeight: 600, display: "block", marginBottom: 4, textTransform: "uppercase", letterSpacing: 0.5 }}>
                    {f.label}
                  </label>
                  <select name={f.key} value={form[f.key] || ""} onChange={onChange} style={inputStyle}>
                    {f.options.map(o => <option key={o} value={o}>{o}</option>)}
                  </select>
                </div>
              ))}
              <div style={{ gridColumn: "1 / -1" }}>
                <label style={{ display: "flex", alignItems: "center", gap: 8, cursor: "pointer", fontSize: 13, color: "#475569" }}>
                  <input type="checkbox" name="is_new_device" checked={form.is_new_device || false} onChange={onChange}
                    style={{ width: 16, height: 16, cursor: "pointer" }} />
                  New / unrecognized device
                </label>
              </div>
            </div>

            {error && (
              <div style={{ marginTop: 12, padding: "10px 14px", background: "#fef2f2", border: "1px solid #fca5a5", borderRadius: 8, fontSize: 12, color: "#dc2626" }}>
                ⚠ {error}
              </div>
            )}

            <Button
              onClick={analyze} disabled={loading}
              style={{ width: "100%", marginTop: 16, justifyContent: "center", padding: "11px" }}
            >
              {loading ? <><Spinner size={14} /> Analyzing...</> : "▶  Run Analysis"}
            </Button>
          </div>
        </Card>

        {/* Results */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
          {result ? (
            <>
              {/* Score */}
              <Card title="Risk Assessment">
                <div style={{ padding: "16px 20px" }}>
                  <div style={{ display: "flex", gap: 20, alignItems: "center", marginBottom: 16 }}>
                    <div style={{
                      width: 90, height: 90, borderRadius: "50%",
                      border: `4px solid ${scoreColor}`,
                      display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center",
                      background: `${scoreColor}10`, flexShrink: 0
                    }}>
                      <span style={{ fontSize: 26, fontWeight: 800, color: scoreColor, lineHeight: 1 }}>{score}</span>
                      <span style={{ fontSize: 9, color: scoreColor, opacity: 0.7 }}>/100</span>
                    </div>
                    <div>
                      <ActionBadge action={action} />
                      <div style={{ fontSize: 12, color: "#475569", marginTop: 8, lineHeight: 1.6 }}>
                        {result.response?.alert_message}
                      </div>
                      <div style={{ marginTop: 8 }}>
                        <RiskBadge level={riskLevel} />
                      </div>
                    </div>
                  </div>
                  <RiskBar score={score} showLabel />

                  <div style={{ display: "flex", gap: 10, marginTop: 14 }}>
                    {result.ctr_required && (
                      <span style={{ fontSize: 11, background: "#eff6ff", color: "#2563eb", border: "1px solid #bfdbfe", borderRadius: 5, padding: "3px 8px", fontWeight: 600 }}>
                        📋 CTR Required
                      </span>
                    )}
                    {result.sar_required && (
                      <span style={{ fontSize: 11, background: "#fef2f2", color: "#dc2626", border: "1px solid #fca5a5", borderRadius: 5, padding: "3px 8px", fontWeight: 600 }}>
                        ⚠ SAR Required
                      </span>
                    )}
                  </div>
                </div>
              </Card>

              {/* Fraud Flags */}
              {result.sentry?.fraud_indicators?.length > 0 && (
                <Card title={`🔍 Fraud Indicators (${result.sentry.fraud_indicators.length})`}>
                  <div style={{ padding: "12px 20px" }}>
                    {result.sentry.fraud_indicators.map((f, i) => (
                      <div key={i} style={{ display: "flex", gap: 8, padding: "6px 0", borderBottom: i < result.sentry.fraud_indicators.length - 1 ? "1px solid #f8fafc" : "none", fontSize: 12, color: "#475569" }}>
                        <span style={{ color: "#d97706", flexShrink: 0 }}>⚠</span>{f}
                      </div>
                    ))}
                  </div>
                </Card>
              )}

              {/* Compliance */}
              <Card title="📋 Compliance Checks">
                <div style={{ padding: "12px 20px" }}>
                  {[
                    { k: "KYC Status",   v: result.auditor?.kyc_status },
                    { k: "AML Status",   v: result.auditor?.aml_status },
                    { k: "Watchlist",    v: result.auditor?.watchlist_status },
                    { k: "Compliance",   v: result.auditor?.compliance_status },
                  ].map(({ k, v }) => {
                    const ok = ["VERIFIED","CLEAR","COMPLIANT"].includes(v);
                    const bad = ["FAILED","MATCH_FOUND","NON_COMPLIANT"].includes(v);
                    const color = ok ? "#16a34a" : bad ? "#dc2626" : "#d97706";
                    return (
                      <div key={k} style={{ display: "flex", justifyContent: "space-between", padding: "7px 0", borderBottom: "1px solid #f8fafc", fontSize: 12 }}>
                        <span style={{ color: "#64748b" }}>{k}</span>
                        <span style={{ color, fontWeight: 700 }}>{v}</span>
                      </div>
                    );
                  })}
                  {result.auditor?.regulatory_flags?.length > 0 && (
                    <div style={{ marginTop: 10 }}>
                      {result.auditor.regulatory_flags.map((f, i) => (
                        <div key={i} style={{ fontSize: 11, color: "#ea580c", padding: "3px 0" }}>⚑ {f}</div>
                      ))}
                    </div>
                  )}
                </div>
              </Card>

              {/* Secondary Actions */}
              {result.response?.secondary_actions?.length > 0 && (
                <Card title="⚡ Secondary Actions">
                  <div style={{ padding: "12px 20px", display: "flex", flexWrap: "wrap", gap: 8 }}>
                    {result.response.secondary_actions.map(a => (
                      <span key={a} style={{ fontSize: 11, background: "#fef2f2", color: "#dc2626", border: "1px solid #fca5a5", borderRadius: 5, padding: "4px 10px", fontWeight: 600 }}>
                        {a.replace(/_/g, " ")}
                      </span>
                    ))}
                  </div>
                </Card>
              )}

              {/* Blockchain */}
              <Card title="⛓ Blockchain Record">
                <div style={{ padding: "12px 20px" }}>
                  <div style={{ fontFamily: "monospace", fontSize: 11, color: "#64748b", lineHeight: 2 }}>
                    <div>TX ID: <span style={{ color: "#0f172a" }}>#{result.transaction_id}</span></div>
                    <div>Processing: <span style={{ color: "#0f172a" }}>{result.processing_time_ms}ms</span></div>
                    <div>Timestamp: <span style={{ color: "#0f172a" }}>{result.timestamp?.slice(0, 19).replace("T", " ")} UTC</span></div>
                  </div>
                </div>
              </Card>
            </>
          ) : (
            <Card>
              <div style={{ padding: "48px 24px", textAlign: "center", color: "#94a3b8" }}>
                <div style={{ fontSize: 36, marginBottom: 12 }}>🔍</div>
                <div style={{ fontSize: 14, fontWeight: 600, color: "#475569", marginBottom: 6 }}>
                  Ready to analyze
                </div>
                <div style={{ fontSize: 12 }}>
                  Select a preset or fill in details,<br />then click <strong style={{ color: "#2563eb" }}>Run Analysis</strong>
                </div>
              </div>
            </Card>
          )}
        </div>
      </div>
    </div>
  );
}
