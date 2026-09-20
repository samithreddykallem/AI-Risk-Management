import React from "react";
import ReactMarkdown from "react-markdown";
import { FileText, Download, ArrowLeft } from "lucide-react";

export default function AuditReportPage({ auditResult, onBackToTrace }) {
  if (!auditResult) return null;

  const reportMarkdown = auditResult.audit_report_markdown || "No report generated.";

  const handleDownload = () => {
    const element = document.createElement("a");
    const file = new Blob([reportMarkdown], { type: "text/markdown" });
    element.href = URL.createObjectURL(file);
    element.download = `${auditResult.audit_id}_AI_Audit_Report.md`;
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  return (
    <div className="card">
      <div className="card-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <button className="btn-primary" onClick={onBackToTrace} style={{ padding: "0.5rem 1rem", fontSize: "0.85rem", background: "rgba(255,255,255,0.05)", border: "1px solid var(--border-color)", color: "var(--text-main)" }}>
          <ArrowLeft size={16} /> Back to Adaptive Trace
        </button>

        <div style={{ display: "flex", gap: "1rem" }}>
          <button className="btn-primary" onClick={handleDownload} style={{ padding: "0.5rem 1rem", fontSize: "0.85rem" }}>
            <Download size={16} /> Export Markdown Report
          </button>
        </div>
      </div>

      <div className="markdown-body" style={{ background: "rgba(11,15,25,0.6)", padding: "2rem", borderRadius: "12px", border: "1px solid var(--border-color)" }}>
        <ReactMarkdown>{reportMarkdown}</ReactMarkdown>
      </div>
    </div>
  );
}
