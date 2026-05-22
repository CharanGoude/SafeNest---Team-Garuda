import { useState, useEffect } from "react";
import api from "../utils/api";
import { StatCard, RiskBadge, ActionBadge, RiskBar, Card, Button, EmptyState, ConnectionError, Spinner } from "../components/UI";

export default function Dashboard({ onNavigate }) {
  const [stats, setStats]       = useState(null);
  const [txs, setTxs]           = useState([]);
  const [loading, setLoading]   = useState(true);
  const [simming, setSimming]   = useState(false);
  const [error, setError]       = useState(false);
  const [filterType, setFilterType] = useState("none"); // "none", "single", "range"
  const [selectedDate, setSelectedDate] = useState("");
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");

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

  const filterTransactionsByDate = () => {
    if (filterType === "none") return txs;
    
    if (filterType === "single" && selectedDate) {
      return txs.filter(tx => {
        const txDate = new Date(tx.timestamp).toISOString().split('T')[0];
        return txDate === selectedDate;
      });
    }
    
    if (filterType === "range" && startDate && endDate) {
      return txs.filter(tx => {
        const txDate = new Date(tx.timestamp).toISOString().split('T')[0];
        return txDate >= startDate && txDate <= endDate;
      });
    }
    
    return txs;
  };

  const filteredTxs = filterTransactionsByDate();

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
            { name: "Sentry Agent",     desc: "Fraud pattern detection · Behavioral AI", color: "#d97706", bg: "#fffbeb", icon: "🔍" },
            { name: "Coordinator Agent", desc: "Coordination · Risk aggregation",         color: "#2563eb", bg: "#eff6ff", icon: "📊" },
            { name: "Response Agent",   desc: "Auto-action · Blockchain logging",       color: "#dc2626", bg: "#fef2f2", icon: "⚡" },
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
        {/* Date Filter Section */}
        <div style={{ padding: "0 20px", marginBottom: 20, borderBottom: "1px solid #f1f5f9", paddingBottom: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 700, color: "#475569", marginBottom: 12 }}>
            🔍 Filter Transactions by Date
          </div>
          
          {/* Filter Type Selector */}
          <div style={{ display: "flex", gap: 10, marginBottom: 12, flexWrap: "wrap" }}>
            {[
              { id: "none", label: "All Dates", icon: "📅" },
              { id: "single", label: "Single Date", icon: "📆" },
              { id: "range", label: "Date Range", icon: "📊" }
            ].map(opt => (
              <button
                key={opt.id}
                onClick={() => {
                  setFilterType(opt.id);
                  setSelectedDate("");
                  setStartDate("");
                  setEndDate("");
                }}
                style={{
                  padding: "6px 12px",
                  borderRadius: 6,
                  border: `1px solid ${filterType === opt.id ? "#2563eb" : "#cbd5e1"}`,
                  background: filterType === opt.id ? "#eff6ff" : "#ffffff",
                  color: filterType === opt.id ? "#2563eb" : "#475569",
                  fontSize: 11,
                  fontWeight: 600,
                  cursor: "pointer",
                  transition: "all 0.2s",
                  display: "flex",
                  alignItems: "center",
                  gap: 4
                }}
              >
                <span>{opt.icon}</span> {opt.label}
              </button>
            ))}
          </div>

          {/* Filter Input Fields */}
          <div style={{ display: "flex", gap: 12, alignItems: "flex-end", flexWrap: "wrap" }}>
            {filterType === "single" && (
              <>
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <label style={{ fontSize: 11, fontWeight: 600, color: "#475569" }}>Select Date</label>
                  <input
                    type="date"
                    value={selectedDate}
                    onChange={(e) => setSelectedDate(e.target.value)}
                    style={{
                      padding: "8px 12px",
                      borderRadius: 6,
                      border: "1px solid #e2e8f0",
                      fontSize: 12,
                      fontFamily: "inherit",
                      backgroundColor: "#ffffff",
                      cursor: "pointer",
                      transition: "border 0.2s",
                      boxShadow: selectedDate ? "0 0 0 2px #eff6ff" : "none"
                    }}
                  />
                </div>
                {selectedDate && (
                  <button
                    onClick={() => setSelectedDate("")}
                    style={{
                      padding: "6px 12px",
                      borderRadius: 6,
                      border: "1px solid #fecaca",
                      background: "#fef2f2",
                      color: "#dc2626",
                      fontSize: 11,
                      cursor: "pointer",
                      fontWeight: 600,
                      transition: "all 0.2s"
                    }}
                  >
                    ✕ Clear Filter
                  </button>
                )}
              </>
            )}

            {filterType === "range" && (
              <>
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <label style={{ fontSize: 11, fontWeight: 600, color: "#475569" }}>From Date</label>
                  <input
                    type="date"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    style={{
                      padding: "8px 12px",
                      borderRadius: 6,
                      border: "1px solid #e2e8f0",
                      fontSize: 12,
                      fontFamily: "inherit",
                      backgroundColor: "#ffffff",
                      cursor: "pointer"
                    }}
                  />
                </div>
                <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                  <label style={{ fontSize: 11, fontWeight: 600, color: "#475569" }}>To Date</label>
                  <input
                    type="date"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    style={{
                      padding: "8px 12px",
                      borderRadius: 6,
                      border: "1px solid #e2e8f0",
                      fontSize: 12,
                      fontFamily: "inherit",
                      backgroundColor: "#ffffff",
                      cursor: "pointer"
                    }}
                  />
                </div>
                {(startDate || endDate) && (
                  <button
                    onClick={() => {
                      setStartDate("");
                      setEndDate("");
                    }}
                    style={{
                      padding: "6px 12px",
                      borderRadius: 6,
                      border: "1px solid #fecaca",
                      background: "#fef2f2",
                      color: "#dc2626",
                      fontSize: 11,
                      cursor: "pointer",
                      fontWeight: 600,
                      transition: "all 0.2s"
                    }}
                  >
                    ✕ Clear Filter
                  </button>
                )}
              </>
            )}

            {/* Results Summary */}
            {filterType !== "none" && (
              <div style={{ marginLeft: "auto", fontSize: 11, color: "#94a3b8", fontWeight: 500 }}>
                Showing <span style={{ color: "#2563eb", fontWeight: 700 }}>{filteredTxs.length}</span> of <span style={{ color: "#475569", fontWeight: 600 }}>{txs.length}</span> transactions
              </div>
            )}
          </div>
        </div>

        {filteredTxs.length === 0 && txs.length > 0 ? (
          <EmptyState
            icon="📭"
            title="No transactions on this date"
            subtitle="Try selecting a different date"
          />
        ) : txs.length === 0 ? (
          <EmptyState
            icon="📭"
            title="No transactions yet"
            subtitle="Click Simulate to generate demo transactions"
            action={<Button onClick={simulate} disabled={simming}>▶ Simulate Now</Button>}
          />
        ) : (
          <div>
            {filteredTxs.map((tx, i) => {
              const txDate = new Date(tx.timestamp);
              const formattedDate = txDate.toLocaleDateString('en-IN', { month: 'short', day: 'numeric', year: 'numeric' });
              const formattedTime = txDate.toLocaleTimeString('en-IN', { hour: '2-digit', minute: '2-digit' });
              
              return (
                <div key={tx.transaction_id} style={{
                  display: "flex", alignItems: "center", gap: 14,
                  padding: "12px 20px",
                  borderBottom: i < filteredTxs.length - 1 ? "1px solid #f8fafc" : "none",
                  transition: "background 0.1s"
                }}>
                  <div style={{ minWidth: 80 }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: "#0f172a", fontFamily: "monospace" }}>
                      #{tx.transaction_id}
                    </div>
                    <div style={{ fontSize: 10, color: "#94a3b8" }}>{formattedDate}</div>
                    <div style={{ fontSize: 10, color: "#cbd5e1" }}>{formattedTime}</div>
                  </div>
                  <div style={{ flex: 1, minWidth: 0 }}>
                    <div style={{ fontSize: 12, color: "#0f172a", fontWeight: 500, marginBottom: 3 }}>{tx.user_id}</div>
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
              );
            })}
          </div>
        )}
      </Card>
    </div>
  );
}
