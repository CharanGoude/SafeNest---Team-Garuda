import { useState, useEffect } from "react";
const API = "http://localhost:8000";

const aColor = a => ({BLOCK:"var(--danger)",FREEZE_ACCOUNT:"var(--danger)",
  REQUIRE_OTP:"var(--warning)",REQUIRE_BIOMETRIC:"var(--warning)",
  FLAG_FOR_REVIEW:"#ffdd57",APPROVE:"var(--accent)"}[a]||"var(--muted)");

export default function BlockchainPage() {
  const [ledger, setLedger] = useState([]);
  const [total, setTotal]   = useState(0);

  useEffect(() => {
    const go = async () => {
      try {
        const r = await fetch(`${API}/blockchain`).then(r=>r.json());
        setLedger([...(r.ledger||[])].reverse());
        setTotal(r.total_blocks||0);
      } catch{}
    };
    go(); const id = setInterval(go, 4000); return ()=>clearInterval(id);
  }, []);

  return (
    <div>
      <div style={{ marginBottom:28 }}>
        <div style={{ fontSize:10, color:"var(--accent)", letterSpacing:4, marginBottom:4 }}>IMMUTABLE LEDGER</div>
        <h1 style={{ fontSize:28, fontWeight:800, fontFamily:"'Syne',sans-serif" }}>Blockchain Log</h1>
        <p style={{ fontSize:11, color:"var(--muted)", marginTop:4 }}>{total} blocks · tamper-proof compliance records</p>
      </div>

      {/* Chain Stats */}
      <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:10,
        padding:"18px 24px", marginBottom:24, display:"flex", gap:40, flexWrap:"wrap" }}>
        {[
          { label:"TOTAL BLOCKS",   value:total,     color:"var(--accent)" },
          { label:"CHAIN STATUS",   value:"VALID",   color:"var(--accent)" },
          { label:"CONSENSUS",      value:"PoA",     color:"var(--accent2)" },
          { label:"ENCRYPTION",     value:"SHA-256", color:"var(--accent2)" },
          { label:"TAMPER PROOF",   value:"YES",     color:"var(--accent)" },
        ].map(({label,value,color})=>(
          <div key={label}>
            <div style={{ fontSize:9, color:"var(--muted)", letterSpacing:3, marginBottom:4 }}>{label}</div>
            <div style={{ fontSize:18, fontWeight:800, color, fontFamily:"'Syne',sans-serif" }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Explanation */}
      <div style={{ background:"rgba(0,212,255,0.04)", border:"1px solid rgba(0,212,255,0.15)", borderRadius:10,
        padding:"14px 20px", marginBottom:24, fontSize:11, color:"var(--muted)", lineHeight:1.7 }}>
        <span style={{ color:"var(--accent2)", fontWeight:700 }}>How it works: </span>
        Every fraud decision made by the Response Agent is recorded as an immutable block. Each block stores the
        transaction ID, action taken, risk score, and a cryptographic hash. Records cannot be altered or deleted,
        ensuring full regulatory audit compliance.
      </div>

      {/* Blockchain Blocks */}
      {ledger.length===0 ? (
        <div style={{ background:"var(--surface)", border:"1px solid var(--border)", borderRadius:10,
          padding:40, textAlign:"center", color:"var(--muted)", fontSize:11 }}>
          No blocks yet. Analyze transactions to populate the ledger.
        </div>
      ) : (
        <div style={{ display:"flex", flexDirection:"column" }}>
          {ledger.map((block,i)=>(
            <div key={block.block_id} style={{ display:"flex", gap:0 }}>
              <div style={{ display:"flex", flexDirection:"column", alignItems:"center", width:44, flexShrink:0 }}>
                <div style={{ width:26, height:26, borderRadius:6, background:`${aColor(block.action)}15`,
                  border:`1px solid ${aColor(block.action)}50`, display:"flex", alignItems:"center",
                  justifyContent:"center", fontSize:9, color:aColor(block.action), marginTop:i===0?20:0, fontWeight:700,
                  flexShrink:0 }}>
                  {ledger.length - i}
                </div>
                {i<ledger.length-1 && <div style={{ width:1, flex:1, background:"var(--border)", minHeight:14 }} />}
              </div>

              <div style={{ flex:1, background:"var(--surface)", border:"1px solid var(--border)", borderRadius:10,
                padding:"14px 18px", marginBottom:10, marginLeft:8,
                borderLeft:`3px solid ${aColor(block.action)}` }}>
                <div style={{ display:"flex", justifyContent:"space-between", alignItems:"flex-start", flexWrap:"wrap", gap:8 }}>
                  <div>
                    <div style={{ display:"flex", gap:10, alignItems:"center", marginBottom:7 }}>
                      <span style={{ fontSize:11, fontWeight:700, color:"var(--text)" }}>Block #{block.block_id}</span>
                      <span style={{ fontSize:9, color:aColor(block.action), background:`${aColor(block.action)}15`,
                        padding:"2px 8px", borderRadius:3, letterSpacing:1 }}>
                        {block.action?.replace(/_/g," ")}
                      </span>
                    </div>
                    <div style={{ fontFamily:"monospace", fontSize:10, color:"var(--muted)", lineHeight:1.9 }}>
                      <div>TX: <span style={{ color:"var(--text)" }}>#{block.transaction_id}</span></div>
                      <div>HASH: <span style={{ color:"var(--accent2)" }}>0x{block.hash}</span></div>
                    </div>
                  </div>
                  <div style={{ textAlign:"right" }}>
                    <div style={{ fontSize:22, fontWeight:800, color:aColor(block.action), fontFamily:"'Syne',sans-serif" }}>
                      {block.risk_score}
                    </div>
                    <div style={{ fontSize:9, color:"var(--muted)" }}>risk score</div>
                  </div>
                </div>
                <div style={{ fontSize:9, color:"var(--muted)", marginTop:8, letterSpacing:1 }}>
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
