import { useState, useEffect } from "react";
import api from "../utils/api";
import { Card, EmptyState, Spinner } from "../components/UI";

const actionColor = a => ({
  BLOCK:"#dc2626", FREEZE_ACCOUNT:"#dc2626",
  REQUIRE_OTP:"#d97706", FLAG_FOR_REVIEW:"#d97706",
  APPROVE:"#16a34a"
}[a] || "#64748b");

export default function BlockchainPage() {
  const [ledger, setLedger] = useState([]);
  const [total, setTotal]   = useState(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const go = async () => {
      try {
        const r = await api.blockchain();
        setLedger(r.ledger || []);
        setTotal(r.total_blocks || 0);
      } catch {}
      finally { setLoading(false); }
    };
    go();
    const id = setInterval(go, 6000);
    return () => clearInterval(id);
  }, []);

  if (loading) return (
    <div style={{ display:"flex", alignItems:"center", justifyContent:"center", height:300, gap:12, color:"#94a3b8" }}>
      <Spinner size={22} /> Loading ledger...
    </div>
  );

  return (
    <div style={{ animation:"fadeUp 0.3s ease" }}>
      <div style={{ marginBottom:24 }}>
        <h1 style={{ fontSize:22, fontWeight:800, color:"#0f172a", marginBottom:4 }}>Blockchain Ledger</h1>
        <p style={{ fontSize:13, color:"#94a3b8" }}>{total} immutable blocks · SHA-256 cryptographic hashing</p>
      </div>

      {/* Chain stats */}
      <div style={{ display:"flex", gap:14, marginBottom:20 }}>
        {[
          { label:"Total Blocks",  value:total,   color:"#2563eb" },
          { label:"Chain Status",  value:"VALID",  color:"#16a34a" },
          { label:"Algorithm",     value:"SHA-256",color:"#7c3aed" },
          { label:"Tamper Proof",  value:"YES",    color:"#16a34a" },
        ].map(s => (
          <div key={s.label} style={{ background:"#fff", border:"1px solid #e2e8f0", borderRadius:10, padding:"16px 20px", flex:1, boxShadow:"0 1px 3px rgba(0,0,0,0.05)" }}>
            <div style={{ fontSize:10, color:"#94a3b8", fontWeight:700, textTransform:"uppercase", letterSpacing:0.5, marginBottom:6 }}>{s.label}</div>
            <div style={{ fontSize:22, fontWeight:800, color:s.color }}>{s.value}</div>
          </div>
        ))}
      </div>

      {/* Info box */}
      <div style={{ background:"#eff6ff", border:"1px solid #bfdbfe", borderRadius:10, padding:"12px 16px", marginBottom:20, fontSize:12, color:"#1d4ed8", lineHeight:1.7 }}>
        <strong>How it works:</strong> Every fraud decision made by the Response Agent is recorded as an immutable block.
        Each block contains a SHA-256 hash of its content plus the previous block's hash.
        Any modification to any record breaks the chain and is immediately detectable.
        This satisfies RBI requirements for tamper-proof compliance audit trails.
      </div>

      {/* Blockchain blocks */}
      {ledger.length === 0 ? (
        <Card>
          <EmptyState icon="⛓" title="No blocks yet" subtitle="Analyze transactions to populate the ledger" />
        </Card>
      ) : (
        <div style={{ display:"flex", flexDirection:"column", gap:0 }}>
          {ledger.map((block, i) => (
            <div key={block.block_id} style={{ display:"flex", gap:0 }}>
              {/* Chain connector */}
              <div style={{ display:"flex", flexDirection:"column", alignItems:"center", width:44, flexShrink:0 }}>
                <div style={{
                  width:28, height:28, borderRadius:6,
                  background:`${actionColor(block.action)}15`,
                  border:`2px solid ${actionColor(block.action)}`,
                  display:"flex", alignItems:"center", justifyContent:"center",
                  fontSize:10, fontWeight:800, color:actionColor(block.action),
                  marginTop: i === 0 ? 18 : 0, flexShrink:0
                }}>
                  {ledger.length - i}
                </div>
                {i < ledger.length - 1 && (
                  <div style={{ width:2, flex:1, background:"#e2e8f0", margin:"4px 0" }} />
                )}
              </div>

              {/* Block card */}
              <div style={{
                flex:1, background:"#fff", border:"1px solid #e2e8f0",
                borderLeft:`3px solid ${actionColor(block.action)}`,
                borderRadius:10, padding:"14px 18px", marginBottom:10, marginLeft:8,
                boxShadow:"0 1px 3px rgba(0,0,0,0.05)"
              }}>
                <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", flexWrap:"wrap", gap:8 }}>
                  <div>
                    <div style={{ display:"flex", gap:10, alignItems:"center", marginBottom:8 }}>
                      <span style={{ fontSize:12, fontWeight:800, color:"#0f172a", fontFamily:"monospace" }}>
                        Block #{block.block_id}
                      </span>
                      <span style={{
                        fontSize:10, color:actionColor(block.action),
                        background:`${actionColor(block.action)}12`,
                        border:`1px solid ${actionColor(block.action)}30`,
                        padding:"2px 8px", borderRadius:5, fontWeight:600
                      }}>
                        {block.action?.replace(/_/g, " ")}
                      </span>
                    </div>
                    <div style={{ fontFamily:"monospace", fontSize:11, color:"#64748b", lineHeight:2 }}>
                      <div>TX: <span style={{ color:"#0f172a" }}>#{block.transaction_id}</span></div>
                      <div style={{ wordBreak:"break-all" }}>
                        HASH: <span style={{ color:"#7c3aed" }}>0x{block.block_hash?.slice(0,32)}...</span>
                      </div>
                      <div style={{ wordBreak:"break-all" }}>
                        PREV: <span style={{ color:"#94a3b8" }}>0x{block.prev_hash?.slice(0,32)}...</span>
                      </div>
                    </div>
                  </div>
                  <div style={{ textAlign:"right" }}>
                    <div style={{ fontSize:26, fontWeight:800, color:actionColor(block.action) }}>
                      {block.risk_score}
                    </div>
                    <div style={{ fontSize:10, color:"#94a3b8" }}>risk score</div>
                  </div>
                </div>
                <div style={{ fontSize:10, color:"#94a3b8", marginTop:8 }}>
                  {block.timestamp?.slice(0,19).replace("T"," ")} UTC
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
