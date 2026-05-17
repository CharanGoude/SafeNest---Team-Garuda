import { useState, useEffect } from "react";
import api from "../utils/api";
import { StatCard, RiskBadge, ActionBadge, RiskBar, Card, Button, EmptyState, ConnectionError, Spinner } from "../components/UI";

export default function Dashboard({ onNavigate }) {
  const [stats, setStats]       = useState(null);
  const [txs, setTxs]           = useState([]);
  const [loading, setLoading]   = useState(true);
  const [simming, setSimming]   = useState(false);
  const [error, setError]       = useState(false);

  const fetchAll = async () => {
    try {
      const [s, t] = await Promise.all([
        api.stats(),
        api.transactions({ limit: 8 })
      ]);
      setStats(s);
      setTxs(t.transactions || []);
      setError(false);
    } catch { setError(true); }
    finally { setLoading(false); }
  };

  useEffect(() => {
    fetchAll();
    const id = setInterval(fetchAll, 8000);
    return () => clearInterval(id);
  }, []);

  const simulate = async () => {
    setSimming(true);
    try { await api.simulate(6); await fetchAll(); }
    catch (e) { setError(true); }
    finally { setSimming(false); }
  };

  if (loading) return (
    <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 300, gap: 12, color: "#94a3b8" }}>
      <Spinner size={22} /> Loading dashboard...
    </div>
  );

  return (
    <div style={{ animation: "fadeUp 0.3s ease" }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 24 }}>
        <div>
          <h1 style={{ fontSize: 22, fontWeight: 800, color: "#0f172a", marginBottom: 4 }}>
            Overview
          </h1>
          <p style={{ fontSize: 13, color: "#94a3b8" }}>
            Real-time fraud intelligence · 3 agents active
          </p>
        </div>
        <Button onClick={simulate} disabled={simming} variant="primary">
          {simming ? <><Spinner size={14} /> Running...</> : <><span>▶</span> Simulate 6 TX</>}
        </Button>
      </div>

      {error && <ConnectionError />}

      {/* Stats */}
      {stats && (
        <div style={{ display: "flex", gap: 14, marginBottom: 24, flexWrap: "wrap" }}>
          <StatCard label="Total Analyzed"  value={stats.total}            sub="all time"       color="#2563eb" icon="📊" />
          <StatCard label="Approved"        value={stats.approved}         sub="safe"           color="#16a34a" icon="✓" />
          <StatCard label="Blocked"         value={stats.blocked}          sub="critical"       color="#dc2626" icon="🔒" />
          <StatCard label="Frozen"          value={stats.frozen}           sub="high risk"      color="#ea580c" icon="❄" />
          <StatCard label="OTP Triggered"   value={stats.otp}              sub="challenged"     color="#d97706" icon="📱" />
          <StatCard label="Fraud Rate"      value={`${stats.fraud_rate}%`} sub="of total"       color={stats.fraud_rate > 50 ? "#dc2626" : "#d97706"} icon="📈" />
          <StatCard label="Avg Risk Score"  value={stats.avg_risk}         sub="out of 100"     color="#7c3aed" icon="⚡" />
          <StatCard label="CTR Filed"       value={stats.ctr_count}        sub="regulatory"     color="#0891b2" icon="📋" />
        </div>
      )}

      {/* Agent Pipeline */}
      <Card title="3-Agent Pipeline" style={{ marginBottom: 20, padding: "20px" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 0, overflowX: "auto", paddingTop: 4 }}>
          {[
            { name: "Sentry Agent",   desc: "Fraud detection · Behavioral AI",    color: "#d97706", bg: "#fffbeb", icon: "🔍" },
            { name: "Auditor Agent",  desc: "KYC · AML · Watchlist · CTR/SAR",   color: "#2563eb", bg: "#eff6ff", icon: "📋" },
            { name: "Response Agent", desc: "Auto-action · Blockchain logging",   color: "#dc2626", bg: "#fef2f2", icon: "⚡" },
          ].map((a, i, arr) => (
            <div key={a.name} style={{ display: "flex", alignItems: "center" }}>
              <div style={{
                background: a.bg, border: `1px solid ${a.color}30`,
                borderTop: `3px solid ${a.color}`, borderRadius: 8,
                padding: "14px 18px", textAlign: "center", minWidth: 160
              }}>
                <div style={{ fontSize: 22, marginBottom: 6 }}>{a.icon}</div>
                <div style={{ fontSize: 12, color: a.color, fontWeight: 700 }}>{a.name}</div>
                <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 3 }}>{a.desc}</div>
              </div>
              {i < arr.length - 1 && (
                <div style={{ padding: "0 12px", color: "#cbd5e1", fontSize: 20 }}>→</div>
              )}
            </div>
          ))}
        </div>
      </Card>

      {/* Recent Transactions */}
      <Card
        title="Recent Transactions"
        action={
          <Button variant="ghost" size="sm" onClick={() => onNavigate("transactions")}>
            View all →
          </Button>
        }
      >
        {txs.length === 0 ? (
          <EmptyState
            icon="📭"
            title="No transactions yet"
            subtitle="Click Simulate to generate demo transactions"
            action={<Button onClick={simulate} disabled={simming}>▶ Simulate Now</Button>}
          />
        ) : (
          <div>
            {txs.map((tx, i) => (
              <div key={tx.transaction_id} style={{
                display: "flex", alignItems: "center", gap: 14,
                padding: "12px 20px",
                borderBottom: i < txs.length - 1 ? "1px solid #f8fafc" : "none",
                transition: "background 0.1s"
              }}>
                <div style={{ minWidth: 70 }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a", fontFamily: "monospace" }}>
                    #{tx.transaction_id}
                  </div>
                  <div style={{ fontSize: 11, color: "#94a3b8" }}>{tx.user_id}</div>
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 12, color: "#475569", marginBottom: 5, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {tx.merchant_name} · {tx.location_country}
                  </div>
                  <RiskBar score={tx.final_risk_score} />
                </div>
                <div style={{ textAlign: "right", flexShrink: 0, minWidth: 80 }}>
                  <div style={{ fontSize: 14, fontWeight: 700, color: "#0f172a" }}>
                    ₹{tx.amount?.toFixed(2)}
                  </div>
                  <div style={{ fontSize: 11, color: "#94a3b8" }}>{tx.currency}</div>
                </div>
                <div style={{ flexShrink: 0 }}>
                  <RiskBadge level={tx.risk_level} />
                </div>
                <div style={{ flexShrink: 0 }}>
                  <ActionBadge action={tx.action} />
                </div>
              </div>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
}
