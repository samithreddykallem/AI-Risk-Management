import React from "react";
import { Database, ShieldAlert, GitBranch, BarChart3, AlertTriangle } from "lucide-react";

export default function DatasetVisualizer({ profile }) {
  if (!profile) return null;

  return (
    <div className="card">
      <div className="card-header">
        <h3 className="card-title">
          <Database className="w-5 h-5 text-cyan-400" />
          Dataset Profile Overview — {profile.file_name}
        </h3>
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", marginBottom: "1.5rem" }}>
        <div style={{ background: "rgba(11,15,25,0.6)", padding: "1rem", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Total Rows</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "800", color: "var(--accent-cyan)" }}>{profile.row_count}</div>
        </div>
        <div style={{ background: "rgba(11,15,25,0.6)", padding: "1rem", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Total Features</div>
          <div style={{ fontSize: "1.5rem", fontWeight: "800", color: "var(--accent-blue)" }}>{profile.column_count}</div>
        </div>
        <div style={{ background: "rgba(11,15,25,0.6)", padding: "1rem", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Target Attribute</div>
          <div style={{ fontSize: "1.1rem", fontWeight: "700", color: "var(--accent-green)" }}>{profile.target_candidate || "Unspecified"}</div>
        </div>
        <div style={{ background: "rgba(11,15,25,0.6)", padding: "1rem", borderRadius: "10px", border: "1px solid var(--border-color)" }}>
          <div style={{ fontSize: "0.8rem", color: "var(--text-muted)" }}>Audit Mode</div>
          <div style={{ fontSize: "0.95rem", fontWeight: "700", color: "var(--accent-purple)" }}>{profile.audit_mode}</div>
        </div>
      </div>

      {/* Sensitive Attributes & Proxies */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))", gap: "1.5rem" }}>
        <div style={{ background: "rgba(11,15,25,0.4)", padding: "1.25rem", borderRadius: "12px", border: "1px solid var(--border-color)" }}>
          <h4 style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.95rem", fontWeight: "700", color: "var(--accent-orange)", marginBottom: "0.75rem" }}>
            <ShieldAlert size={18} />
            Potentially Sensitive Attributes ({profile.sensitive_candidates.length})
          </h4>
          <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {profile.sensitive_candidates.map((s, idx) => (
              <li key={idx} style={{ background: "rgba(255,158,0,0.08)", padding: "0.5rem 0.75rem", borderRadius: "6px", fontSize: "0.85rem", border: "1px solid rgba(255,158,0,0.2)" }}>
                <strong>{s.column_name}</strong> — <span style={{ color: "var(--text-muted)" }}>{s.category} ({s.tag})</span>
              </li>
            ))}
          </ul>
        </div>

        <div style={{ background: "rgba(11,15,25,0.4)", padding: "1.25rem", borderRadius: "12px", border: "1px solid var(--border-color)" }}>
          <h4 style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.95rem", fontWeight: "700", color: "var(--accent-purple)", marginBottom: "0.75rem" }}>
            <GitBranch size={18} />
            Proxy Candidates Identified ({profile.proxy_candidates.length})
          </h4>
          <ul style={{ listStyle: "none", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
            {profile.proxy_candidates.map((p, idx) => (
              <li key={idx} style={{ background: "rgba(157,78,221,0.08)", padding: "0.5rem 0.75rem", borderRadius: "6px", fontSize: "0.85rem", border: "1px solid rgba(157,78,221,0.2)" }}>
                <strong>{p.proxy_column}</strong> <span style={{ color: "var(--text-muted)" }}>(associated with {p.sensitive_column}, score={p.strength_score})</span>
              </li>
            ))}
            {profile.proxy_candidates.length === 0 && (
              <li style={{ color: "var(--text-dim)", fontSize: "0.85rem" }}>No feature proxy associations detected above threshold.</li>
            )}
          </ul>
        </div>
      </div>
    </div>
  );
}
