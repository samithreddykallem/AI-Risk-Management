import React, { useState } from "react";
import { Upload, FileText, Sparkles, AlertCircle, Database, Shield, Play } from "lucide-react";
import { uploadDataset, runAudit } from "../services/api";

export default function NewAuditPage({ onAuditComplete }) {
  const [projectName, setProjectName] = useState("Smart Credit Decision System");
  const [description, setDescription] = useState("An automated credit risk decisioning engine evaluating consumer loan applications.");
  const [githubUrl, setGithubUrl] = useState("https://github.com/example/credit-decision-system");
  const [documentation, setDocumentation] = useState("Evaluates applicant income, credit score, zip code, and employment status to issue loan recommendations.");

  const [file, setFile] = useState(null);
  const [targetColumn, setTargetColumn] = useState("Loan_Status");
  const [sensitiveAttrs, setSensitiveAttrs] = useState("Gender, Age, ZIP_Code");
  const [predictionsFile, setPredictionsFile] = useState(null);
  const [modelFile, setModelFile] = useState(null);

  const [isUploading, setIsUploading] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Compute Mode Badge
  let mode = "MODE A — DATASET ONLY";
  if (modelFile) mode = "MODE C — DATASET + MODEL ARTIFACT";
  else if (predictionsFile) mode = "MODE B — DATASET + PREDICTIONS";

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      let uploadedDatasetPath = null;
      let uploadedDatasetName = null;

      if (file) {
        setIsUploading(true);
        const uploadRes = await uploadDataset(file);
        uploadedDatasetPath = uploadRes.dataset_path;
        uploadedDatasetName = uploadRes.file_name;
        setIsUploading(false);
      }

      const sensList = sensitiveAttrs
        .split(",")
        .map((s) => s.trim())
        .filter((s) => s.length > 0);

      const auditPayload = {
        project: {
          project_name: projectName,
          description: description,
          github_url: githubUrl || null,
          documentation: documentation || null,
          dataset_path: uploadedDatasetPath,
          dataset_name: uploadedDatasetName || (file ? file.name : null),
          target_column: targetColumn || null,
          sensitive_attributes: sensList
        },
        max_iterations: 3
      };

      const result = await runAudit(auditPayload);
      onAuditComplete(result);
    } catch (err) {
      console.error("Audit launch failed:", err);
      setError(err.message || "Failed to launch adaptive audit.");
    } finally {
      setIsLoading(false);
      setIsUploading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-header" style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <div>
          <h2 className="card-title">
            <Sparkles className="w-6 h-6 text-cyan-400" />
            New Adaptive AI Audit
          </h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginTop: "0.25rem" }}>
            Upload the actual dataset used by your AI system to run an evidence-driven, adaptive risk audit.
          </p>
        </div>
        <div className="mode-badge">{mode}</div>
      </div>

      {error && (
        <div style={{ background: "rgba(239,68,68,0.1)", border: "1px solid #ef4444", borderRadius: "10px", padding: "1rem", color: "#f87171", marginBottom: "1.5rem", display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <AlertCircle size={20} />
          <span>{error}</span>
        </div>
      )}

      <form onSubmit={handleSubmit} className="form-grid">
        <div className="form-group">
          <label>Project Name *</label>
          <input type="text" value={projectName} onChange={(e) => setProjectName(e.target.value)} required />
        </div>

        <div className="form-group">
          <label>GitHub / Repository URL</label>
          <input type="text" value={githubUrl} onChange={(e) => setGithubUrl(e.target.value)} placeholder="https://github.com/org/repo" />
        </div>

        <div className="form-group full-width">
          <label>System Description *</label>
          <textarea rows={3} value={description} onChange={(e) => setDescription(e.target.value)} required />
        </div>

        <div className="form-group full-width">
          <label>Technical Documentation</label>
          <textarea rows={2} value={documentation} onChange={(e) => setDocumentation(e.target.value)} />
        </div>

        {/* Dataset Upload Box */}
        <div className="form-group full-width">
          <label>Dataset Upload * (CSV, XLSX, JSON)</label>
          <div className="upload-dropzone">
            <input type="file" accept=".csv, .xlsx, .xls, .json" onChange={handleFileChange} id="dataset-file-input" style={{ display: "none" }} />
            <label htmlFor="dataset-file-input" style={{ cursor: "pointer", display: "flex", flexDirection: "column", alignItems: "center" }}>
              <Upload className="upload-icon" />
              <div style={{ fontWeight: "700", fontSize: "1.05rem", color: "var(--text-main)" }}>
                {file ? file.name : "Choose or drag dataset file here"}
              </div>
              <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", marginTop: "0.25rem" }}>
                Accepted formats: .csv, .xlsx, .json (max 50MB)
              </div>
            </label>
          </div>
        </div>

        <div className="form-group">
          <label>Target / Label Column (Optional / Auto-detected)</label>
          <input type="text" value={targetColumn} onChange={(e) => setTargetColumn(e.target.value)} placeholder="e.g. Loan_Status, approved, y" />
        </div>

        <div className="form-group">
          <label>Sensitive Attributes (Comma Separated)</label>
          <input type="text" value={sensitiveAttrs} onChange={(e) => setSensitiveAttrs(e.target.value)} placeholder="e.g. Gender, Age, ZIP_Code" />
        </div>

        <div className="form-group full-width" style={{ marginTop: "1rem" }}>
          <button type="submit" disabled={isLoading} className="btn-primary" style={{ width: "100%" }}>
            <Play size={18} />
            {isLoading ? (isUploading ? "Uploading Dataset..." : "Running Adaptive AI Audit...") : "Start Adaptive AI Audit"}
          </button>
        </div>
      </form>
    </div>
  );
}
