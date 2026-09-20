import React, { useState } from "react";
import NewAuditPage from "./pages/NewAuditPage";
import AuditTracePage from "./pages/AuditTracePage";
import AuditReportPage from "./pages/AuditReportPage";
import { ShieldCheck, Cpu } from "lucide-react";
import "./styles/dashboard.css";

export default function App() {
  const [currentView, setCurrentView] = useState("new_audit"); // "new_audit" | "trace" | "report"
  const [auditResult, setAuditResult] = useState(null);

  const handleAuditComplete = (result) => {
    setAuditResult(result);
    setCurrentView("trace");
  };

  return (
    <div className="app-container">
      {/* Navbar */}
      <header className="header">
        <div className="logo-section">
          <ShieldCheck className="w-7 h-7 text-cyan-400" />
          <div>
            <div className="logo-title">AI RISK MANAGER</div>
            <div className="logo-subtitle">Adaptive Ethical Auditor for AI Systems</div>
          </div>
        </div>

        <div style={{ display: "flex", gap: "1rem" }}>
          <button
            className="btn-primary"
            onClick={() => setCurrentView("new_audit")}
            style={{
              padding: "0.45rem 1rem",
              fontSize: "0.85rem",
              background: currentView === "new_audit" ? "linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))" : "rgba(255,255,255,0.05)",
              color: currentView === "new_audit" ? "#0b0f19" : "var(--text-main)",
              border: "1px solid var(--border-color)"
            }}
          >
            New Audit
          </button>

          {auditResult && (
            <>
              <button
                className="btn-primary"
                onClick={() => setCurrentView("trace")}
                style={{
                  padding: "0.45rem 1rem",
                  fontSize: "0.85rem",
                  background: currentView === "trace" ? "linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))" : "rgba(255,255,255,0.05)",
                  color: currentView === "trace" ? "#0b0f19" : "var(--text-main)",
                  border: "1px solid var(--border-color)"
                }}
              >
                Adaptive Trace
              </button>
              <button
                className="btn-primary"
                onClick={() => setCurrentView("report")}
                style={{
                  padding: "0.45rem 1rem",
                  fontSize: "0.85rem",
                  background: currentView === "report" ? "linear-gradient(135deg, var(--accent-cyan), var(--accent-blue))" : "rgba(255,255,255,0.05)",
                  color: currentView === "report" ? "#0b0f19" : "var(--text-main)",
                  border: "1px solid var(--border-color)"
                }}
              >
                Audit Report
              </button>
            </>
          )}
        </div>
      </header>

      {/* Main Container */}
      <main className="main-content">
        {currentView === "new_audit" && <NewAuditPage onAuditComplete={handleAuditComplete} />}
        {currentView === "trace" && <AuditTracePage auditResult={auditResult} onShowReport={() => setCurrentView("report")} />}
        {currentView === "report" && <AuditReportPage auditResult={auditResult} onBackToTrace={() => setCurrentView("trace")} />}
      </main>
    </div>
  );
}
