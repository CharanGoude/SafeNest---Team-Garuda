/**
 * SafeNest v2.0 — Shared UI Components
 */

// ── RiskBadge ────────────────────────────────────────────────────────────────

export function RiskBadge({ level }) {
  const map = {
    CRITICAL: { bg: "#fef2f2", color: "#dc2626", border: "#fca5a5" },
    HIGH:     { bg: "#fff7ed", color: "#c2410c", border: "#fdba74" },
    MEDIUM:   { bg: "#fffbeb", color: "#b45309", border: "#fcd34d" },
    LOW:      { bg: "#f0fdf4", color: "#15803d", border: "#86efac" },
  };
  const s = map[level] || map.LOW;
  return (
    <span style={{
      background: s.bg, color: s.color, border: `1px solid ${s.border}`,
      borderRadius: 6, padding: "2px 8px", fontSize: 11, fontWeight: 600, letterSpacing: 0.5
    }}>{level}</span>
  );
}

// ── ActionBadge ───────────────────────────────────────────────────────────────

export function ActionBadge({ action }) {
  const map = {
    APPROVE:           { bg: "#f0fdf4", color: "#16a34a", icon: "✓" },
    FLAG_FOR_REVIEW:   { bg: "#fffbeb", color: "#d97706", icon: "⚑" },
    REQUIRE_OTP:       { bg: "#fff7ed", color: "#ea580c", icon: "📱" },
    REQUIRE_BIOMETRIC: { bg: "#fdf4ff", color: "#9333ea", icon: "🔐" },
    FREEZE_ACCOUNT:    { bg: "#fef2f2", color: "#dc2626", icon: "🔒" },
    BLOCK:             { bg: "#450a0a", color: "#fca5a5", icon: "✗" },
  };
  const s = map[action] || { bg: "#f1f5f9", color: "#475569", icon: "?" };
  return (
    <span style={{
      background: s.bg, color: s.color, borderRadius: 6,
      padding: "3px 10px", fontSize: 12, fontWeight: 600,
      display: "inline-flex", alignItems: "center", gap: 4
    }}>
      <span>{s.icon}</span>
      <span>{action?.replace(/_/g, " ")}</span>
    </span>
  );
}

// ── RiskBar ───────────────────────────────────────────────────────────────────

export function RiskBar({ score, showLabel = false }) {
  const color = score >= 75 ? "#dc2626"
              : score >= 50 ? "#ea580c"
              : score >= 30 ? "#d97706"
              : "#16a34a";
  return (
    <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
      <div style={{ flex: 1, height: 6, background: "#e2e8f0", borderRadius: 3, overflow: "hidden" }}>
        <div style={{ width: `${score}%`, height: "100%", background: color, borderRadius: 3, transition: "width 0.4s ease" }} />
      </div>
      {showLabel && <span style={{ fontSize: 12, fontWeight: 600, color, minWidth: 28, textAlign: "right" }}>{score}</span>}
    </div>
  );
}

// ── StatCard ──────────────────────────────────────────────────────────────────

export function StatCard({ label, value, sub, color = "#2563eb", icon }) {
  return (
    <div style={{
      background: "#fff", border: "1px solid #e2e8f0", borderRadius: 10,
      padding: "20px 22px", flex: 1, minWidth: 130,
      borderTop: `3px solid ${color}`, boxShadow: "0 1px 3px rgba(0,0,0,0.06)"
    }}>
      <div style={{ fontSize: 11, color: "#94a3b8", fontWeight: 600, letterSpacing: 0.5, textTransform: "uppercase", marginBottom: 8 }}>
        {icon && <span style={{ marginRight: 4 }}>{icon}</span>}{label}
      </div>
      <div style={{ fontSize: 28, fontWeight: 800, color, lineHeight: 1 }}>{value}</div>
      {sub && <div style={{ fontSize: 11, color: "#94a3b8", marginTop: 4 }}>{sub}</div>}
    </div>
  );
}

// ── Card ──────────────────────────────────────────────────────────────────────

export function Card({ children, style = {}, title, action }) {
  return (
    <div style={{
      background: "#fff", border: "1px solid #e2e8f0", borderRadius: 10,
      boxShadow: "0 1px 3px rgba(0,0,0,0.06)", ...style
    }}>
      {(title || action) && (
        <div style={{
          display: "flex", justifyContent: "space-between", alignItems: "center",
          padding: "14px 20px", borderBottom: "1px solid #f1f5f9"
        }}>
          {title && <div style={{ fontSize: 13, fontWeight: 700, color: "#0f172a" }}>{title}</div>}
          {action}
        </div>
      )}
      {children}
    </div>
  );
}

// ── Spinner ───────────────────────────────────────────────────────────────────

export function Spinner({ size = 18 }) {
  return (
    <div style={{
      width: size, height: size, border: `2px solid #e2e8f0`,
      borderTopColor: "#2563eb", borderRadius: "50%",
      animation: "spin 0.7s linear infinite", display: "inline-block"
    }} />
  );
}

// ── EmptyState ────────────────────────────────────────────────────────────────

export function EmptyState({ icon = "📭", title, subtitle, action }) {
  return (
    <div style={{ textAlign: "center", padding: "48px 24px" }}>
      <div style={{ fontSize: 40, marginBottom: 12 }}>{icon}</div>
      <div style={{ fontSize: 15, fontWeight: 600, color: "#475569", marginBottom: 4 }}>{title}</div>
      {subtitle && <div style={{ fontSize: 13, color: "#94a3b8", marginBottom: 16 }}>{subtitle}</div>}
      {action}
    </div>
  );
}

// ── Button ────────────────────────────────────────────────────────────────────

export function Button({ children, onClick, disabled, variant = "primary", size = "md", style = {} }) {
  const base = {
    display: "inline-flex", alignItems: "center", gap: 6,
    border: "none", cursor: disabled ? "default" : "pointer",
    fontFamily: "inherit", fontWeight: 600, borderRadius: 8,
    opacity: disabled ? 0.6 : 1, transition: "all 0.15s",
    fontSize: size === "sm" ? 12 : 13,
    padding: size === "sm" ? "6px 12px" : "9px 18px",
  };
  const variants = {
    primary:   { background: "#2563eb", color: "#fff" },
    secondary: { background: "#f1f5f9", color: "#475569" },
    danger:    { background: "#dc2626", color: "#fff" },
    ghost:     { background: "transparent", color: "#475569" },
  };
  return (
    <button onClick={onClick} disabled={disabled}
      style={{ ...base, ...variants[variant], ...style }}>
      {children}
    </button>
  );
}

// ── ConnectionError ───────────────────────────────────────────────────────────

export function ConnectionError() {
  return (
    <div style={{
      background: "#fef2f2", border: "1px solid #fca5a5", borderRadius: 8,
      padding: "12px 16px", marginBottom: 20, fontSize: 12,
      color: "#dc2626", display: "flex", alignItems: "center", gap: 8
    }}>
      <span>⚠</span>
      <span>Cannot connect to SafeNest backend. Run: <code style={{ fontFamily: "monospace", background: "#fee2e2", padding: "1px 4px", borderRadius: 3 }}>uvicorn main:app --reload --port 8000</code></span>
    </div>
  );
}
