/**
 * SafeNest v2.0 — API Client
 * Centralized API calls with API key auth
 */

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";
const API_KEY  = import.meta.env.VITE_API_KEY  || "sk-safenest-demo-key-2026";

const headers = {
  "Content-Type": "application/json",
  "X-API-Key":    API_KEY,
};

async function request(path, options = {}) {
  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    headers: { ...headers, ...options.headers },
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || `HTTP ${res.status}`);
  }
  return res.json();
}

export const api = {
  health:       ()           => request("/health"),
  stats:        ()           => request("/api/v1/stats"),
  analyze:      (tx)         => request("/api/v1/analyze",      { method: "POST", body: JSON.stringify(tx) }),
  simulate:     (count = 5)  => request(`/api/v1/simulate?count=${count}`, { method: "POST" }),
  transactions: (params = {}) => {
    const q = new URLSearchParams(params).toString();
    return request(`/api/v1/transactions${q ? "?" + q : ""}`);
  },
  transaction:  (id)         => request(`/api/v1/transactions/${id}`),
  blockchain:   ()           => request("/api/v1/blockchain"),
};

export function createWebSocket(onMessage) {
  const wsUrl = BASE_URL.replace("http", "ws") + "/ws";
  const ws = new WebSocket(wsUrl);
  ws.onmessage = (e) => {
    try { onMessage(JSON.parse(e.data)); }
    catch (_) {}
  };
  ws.onclose = () => setTimeout(() => createWebSocket(onMessage), 3000);
  return ws;
}

export default api;
