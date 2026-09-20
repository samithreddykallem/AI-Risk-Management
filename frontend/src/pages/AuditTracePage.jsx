import React from "react";
import { GitCommit, ShieldAlert, CheckCircle2, ArrowDown, HelpCircle, Activity } from "lucide-react";
import DatasetVisualizer from "../components/DatasetVisualizer";

export default function AuditTracePage({ auditResult, onShowReport }) {
  if (!auditResult) return null;

  const { audit_id, dataset_profile, hypotheses, investigation_trace, status } = auditResult;

  return (
    <div>
      {/* Dataset Profile Header Card */}
      {dataset_profile && <DatasetVisualizer profile={dataset_profile} />}

      {/* MONEY SHOT: ADAPTIVE INVESTIGATION TRACE */}
      <div className="card" style={{ border: "2px solid var(--accent-cyan)", boxShadow: "0 0 25px rgba(0, 240, 255, 0.15)" }}>
        <div className="card-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
          <div>
            <h2 className="card-title" style={{ color: "var(--accent-cyan)" }}>
              <Activity className="w-6 h-6 text-cyan-400" />
              ADAPTIVE INVESTIGATION TRACE
            </h2>
            <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginTop: "0.25rem" }}>
              Live evidence lineage proving adaptive investigation paths driven by empirical findings and Evidence Critic reviews.
            </p>
          </div>
          <button className="btn-primary" onClick={onShowReport}>
            View Final AI Audit Report
          </button>
        </div>

        {/* Hypotheses Overview Chips */}
        <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap", marginBottom: "1.5rem" }}>
          {hypotheses.map((h, idx) => (
            <div key={idx} style={{ background: "rgba(11,15,25,0.7)", border: "1px solid var(--border-color)", padding: "0.75rem 1rem", borderRadius: "10px", flex: 1, minWidth: "280px" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.35rem" }}>
                <span style={{ fontWeight: "700", color: "var(--accent-cyan)", fontSize: "0.85rem" }}>{h.id}</span>
                <span style={{ fontSize: "0.75rem", padding: "0.15rem 0.5rem", borderRadius: "4px", background: "rgba(0,240,255,0.1)", color: "var(--accent-cyan)", fontWeight: "700" }}>{h.status}</span>
              </div>
              <div style={{ fontSize: "0.9rem", fontWeight: "600" }}>"{h.hypothesis}"</div>
            </div>
          ))}
        </div>

        {/* Lineage Chain Flowchart Steps */}
        <div className="lineage-container">
          {investigation_trace.map((step, idx) => (
            <React.Fragment key={idx}>
              <div className="lineage-step">
                <div className="lineage-header">
                  <div className="lineage-title">
                    Iteration {step.iteration}: {step.investigation_plan.investigation_goal}
                  </div>
                  <span className="lineage-badge">
                    Decision: {step.adaptive_decision.action.toUpperCase()}
                  </span>
                </div>

                {/* Observations */}
                <div style={{ fontSize: "0.9rem", marginBottom: "0.75rem" }}>
                  <strong>Observed Evidence:</strong>
                  <ul style={{ paddingLeft: "1.25rem", marginTop: "0.35rem", color: "var(--text-muted)" }}>
                    {step.observations.map((obs, oIdx) => (
                      <li key={oIdx}>{obs.description || obs.observation}</li>
                    ))}
                  </ul>
                </div>

                {/* Independent Critic Evaluation */}
                {step.critic_evaluation && (
                  <div className="critic-box">
                    <div style={{ fontWeight: "700", color: "var(--accent-purple)", marginBottom: "0.25rem", display: "flex", alignItems: "center", gap: "0.4rem" }}>
                      <ShieldAlert size={16} />
                      Independent Evidence Critic Review:
                    </div>
                    <div>{step.critic_evaluation.reasoning}</div>
                    {step.critic_evaluation.confounding_variables && step.critic_evaluation.confounding_variables.length > 0 && (
                      <div style={{ fontSize: "0.8rem", color: "var(--accent-orange)", marginTop: "0.35rem" }}>
                        Confounding variables flagged for controlled follow-up: {step.critic_evaluation.confounding_variables.join(", ")}
                      </div>
                    )}
                  </div>
                )}

                {/* Adaptive Decision Rationale */}
                <div style={{ marginTop: "0.75rem", fontSize: "0.85rem", color: "var(--text-dim)", fontStyle: "italic" }}>
                  <strong>Adaptive Agent Rationale:</strong> {step.adaptive_decision.reasoning}
                </div>
              </div>

              {idx < investigation_trace.length - 1 && (
                <div style={{ display: "flex", justifyContent: "center", color: "var(--accent-cyan)", margin: "-0.5rem 0" }}>
                  <ArrowDown size={24} />
                </div>
              )}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}
