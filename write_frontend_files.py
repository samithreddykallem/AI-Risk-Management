import os

frontend_dir = r"c:\Users\yerra\OneDrive\Desktop\AI-Risk-Management\frontend\src"

files = {}

# 1. API Client
files[os.path.join(frontend_dir, "services", "api.js")] = '''
const BASE_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8001").replace(/\\/+$/, "");

export async function runAudit(auditRequest) {
  const url = `${BASE_URL}/engine/audit`;
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(auditRequest)
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`Audit Service Error (${response.status}): ${errorText}`);
    }

    return await response.json();
  } catch (err) {
    console.error("API Call Failed:", err);
    throw err;
  }
}

export async function checkBackendHealth() {
  try {
    const response = await fetch(`${BASE_URL}/`);
    return response.ok;
  } catch {
    return false;
  }
}
'''

# 2. Styles
files[os.path.join(frontend_dir, "styles", "dashboard.css")] = '''
:root {
  --bg-primary: #0b0f17;
  --bg-secondary: #131b29;
  --bg-card: #182232;
  --bg-card-hover: #1e2a3e;
  --border-color: #26354a;
  --border-accent: #00f0ff;
  
  --text-main: #f1f5f9;
  --text-muted: #94a3b8;
  --text-dim: #64748b;
  
  --accent-cyan: #06b6d4;
  --accent-blue: #3b82f6;
  --accent-purple: #8b5cf6;
  
  --status-success: #10b981;
  --status-warning: #f59e0b;
  --status-danger: #ef4444;
  --status-info: #3b82f6;
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--bg-primary);
  color: var(--text-main);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  -webkit-font-smoothing: antialiased;
}

.app-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* Header */
.navbar {
  background-color: var(--bg-secondary);
  border-bottom: 1px solid var(--border-color);
  padding: 1rem 2rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.brand {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--accent-cyan), var(--accent-blue));
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  color: #fff;
  font-size: 1.1rem;
  box-shadow: 0 0 12px rgba(6, 182, 212, 0.4);
}

.brand-text h1 {
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
  letter-spacing: -0.5px;
}

.brand-text p {
  font-size: 0.75rem;
  color: var(--accent-cyan);
  font-weight: 500;
}

.nav-links {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.btn {
  padding: 0.6rem 1.2rem;
  border-radius: 6px;
  font-weight: 600;
  font-size: 0.875rem;
  cursor: pointer;
  transition: all 0.2s ease;
  border: 1px solid transparent;
}

.btn-primary {
  background: linear-gradient(135deg, #0284c7, #2563eb);
  color: #fff;
  border-color: #38bdf8;
  box-shadow: 0 0 10px rgba(37, 99, 235, 0.3);
}

.btn-primary:hover {
  background: linear-gradient(135deg, #0369a1, #1d4ed8);
  box-shadow: 0 0 15px rgba(38, 99, 235, 0.5);
}

.btn-secondary {
  background: var(--bg-card);
  color: var(--text-main);
  border-color: var(--border-color);
}

.btn-secondary:hover {
  background: var(--bg-card-hover);
  border-color: var(--text-muted);
}

.btn-outline {
  background: transparent;
  color: var(--accent-cyan);
  border-color: var(--accent-cyan);
}

.btn-outline:hover {
  background: rgba(6, 182, 212, 0.1);
}

/* Main Layout */
.content-wrapper {
  max-width: 1200px;
  width: 100%;
  margin: 0 auto;
  padding: 2rem 1.5rem;
  flex: 1;
}

/* Cards */
.card {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

.card-title {
  font-size: 1.1rem;
  font-weight: 700;
  color: #fff;
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  justify-content: space-between;
  border-bottom: 1px solid var(--border-color);
  padding-bottom: 0.75rem;
}

/* Badges */
.badge {
  padding: 0.2rem 0.6rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-high { background: rgba(239, 68, 68, 0.2); color: #f87171; border: 1px solid #ef4444; }
.badge-medium { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid #f59e0b; }
.badge-low { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid #10b981; }

.badge-observed { background: rgba(59, 130, 246, 0.2); color: #60a5fa; border: 1px solid #3b82f6; }
.badge-inferred { background: rgba(139, 92, 246, 0.2); color: #c084fc; border: 1px solid #8b5cf6; }
.badge-unknown { background: rgba(148, 163, 184, 0.2); color: #cbd5e1; border: 1px solid #64748b; }

.badge-status { background: rgba(6, 182, 212, 0.15); color: #22d3ee; border: 1px solid #06b6d4; }

/* Grid systems */
.grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 1.25rem; }
.grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1.25rem; }

/* Profile KV Pair */
.kv-pair {
  margin-bottom: 0.75rem;
}
.kv-label {
  font-size: 0.8rem;
  color: var(--text-muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.2rem;
}
.kv-value {
  font-size: 0.95rem;
  color: var(--text-main);
}

/* Timeline Flow */
.flow-bar {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  overflow-x: auto;
  padding: 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  margin-bottom: 2rem;
}
.flow-node {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  padding: 0.5rem 0.8rem;
  border-radius: 6px;
  font-size: 0.8rem;
  font-weight: 700;
  white-space: nowrap;
  color: var(--text-muted);
}
.flow-node.active {
  border-color: var(--accent-cyan);
  color: #fff;
  background: rgba(6, 182, 212, 0.1);
  box-shadow: 0 0 10px rgba(6, 182, 212, 0.2);
}
.flow-arrow {
  color: var(--text-dim);
  font-weight: bold;
}

/* Timeline Iterations */
.iteration-card {
  border-left: 3px solid var(--accent-cyan);
  margin-bottom: 1.5rem;
}

.step-box {
  background: rgba(11, 15, 23, 0.6);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 0.8rem 1rem;
  margin-top: 0.75rem;
}

/* Forms */
.form-group {
  margin-bottom: 1.25rem;
}
.form-label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-main);
  margin-bottom: 0.4rem;
}
.form-control {
  width: 100%;
  padding: 0.75rem 1rem;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: 6px;
  color: var(--text-main);
  font-size: 0.95rem;
  font-family: inherit;
  transition: border-color 0.2s;
}
.form-control:focus {
  outline: none;
  border-color: var(--accent-cyan);
}
textarea.form-control {
  min-height: 100px;
  resize: vertical;
}

/* Footer */
.footer {
  border-top: 1px solid var(--border-color);
  padding: 1.5rem;
  text-align: center;
  font-size: 0.8rem;
  color: var(--text-dim);
  background: var(--bg-secondary);
}
'''

# 3. Header Component
files[os.path.join(frontend_dir, "components", "Header.jsx")] = '''
import React from 'react';

export default function Header({ currentRoute, onNavigate }) {
  return (
    <header className="navbar">
      <div className="brand" onClick={() => onNavigate('/')}>
        <div className="logo-icon">🛡️</div>
        <div className="brand-text">
          <h1>AI Risk Manager</h1>
          <p>Adaptive Ethical Auditor for AI Systems</p>
        </div>
      </div>
      <nav className="nav-links">
        <button 
          className={`btn ${currentRoute === '/' ? 'btn-primary' : 'btn-secondary'}`}
          onClick={() => onNavigate('/')}
        >
          Dashboard
        </button>
        <button 
          className={`btn ${currentRoute === '/audit/new' ? 'btn-primary' : 'btn-outline'}`}
          onClick={() => onNavigate('/audit/new')}
        >
          + New Audit
        </button>
      </nav>
    </header>
  );
}
'''

# 4. Landing Page
files[os.path.join(frontend_dir, "pages", "LandingPage.jsx")] = '''
import React from 'react';

export default function LandingPage({ onNavigate }) {
  return (
    <div className="landing-page">
      <div className="card" style={{ textAlign: 'center', padding: '3.5rem 2rem', background: 'linear-gradient(180deg, #131b29 0%, #0b0f17 100%)' }}>
        <h1 style={{ fontSize: '2.5rem', fontWeight: '800', marginBottom: '1rem', color: '#fff' }}>
          AI systems are different. <span style={{ color: '#06b6d4' }}>Their audits should be too.</span>
        </h1>
        <p style={{ fontSize: '1.15rem', color: '#94a3b8', maxWidth: '750px', margin: '0 auto 2rem' }}>
          Traditional AI evaluation uses static domain checklists. AI Risk Manager dynamically analyzes your specific system model, generates evidence-grounded hypotheses, and drives an adaptive investigation loop.
        </p>
        <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center' }}>
          <button className="btn btn-primary" style={{ fontSize: '1.05rem', padding: '0.8rem 2rem' }} onClick={() => onNavigate('/audit/new')}>
            Start New Audit →
          </button>
        </div>
      </div>

      <div className="grid-2" style={{ marginBottom: '2rem' }}>
        <div className="card">
          <div className="card-title">How It Works</div>
          <div className="grid-2" style={{ gap: '1rem' }}>
            <div className="step-box">
              <div style={{ color: '#06b6d4', fontWeight: '700', fontSize: '0.85rem' }}>1. UNDERSTAND</div>
              <p style={{ fontSize: '0.9rem', color: '#cbd5e1', marginTop: '0.3rem' }}>Extracts system purpose, inputs, decision impact & autonomy to build a System Profile.</p>
            </div>
            <div className="step-box">
              <div style={{ color: '#3b82f6', fontWeight: '700', fontSize: '0.85rem' }}>2. HYPOTHESIZE</div>
              <p style={{ fontSize: '0.9rem', color: '#cbd5e1', marginTop: '0.3rem' }}>Formulates plausible, system-grounded risk hypotheses without hardcoded checklists.</p>
            </div>
            <div className="step-box">
              <div style={{ color: '#8b5cf6', fontWeight: '700', fontSize: '0.85rem' }}>3. INVESTIGATE</div>
              <p style={{ fontSize: '0.9rem', color: '#cbd5e1', marginTop: '0.3rem' }}>Designs controlled perturbation probes & executes registered safe tools.</p>
            </div>
            <div className="step-box">
              <div style={{ color: '#10b981', fontWeight: '700', fontSize: '0.85rem' }}>4. ADAPT</div>
              <p style={{ fontSize: '0.9rem', color: '#cbd5e1', marginTop: '0.3rem' }}>Evaluates observations to identify remaining uncertainty and derive the next test.</p>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-title">What Makes AI Risk Manager Different?</div>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.9rem' }}>
            <li style={{ display: 'flex', gap: '0.75rem', fontSize: '0.95rem' }}>
              <span style={{ color: '#06b6d4', fontWeight: 'bold' }}>✓</span>
              <span><strong>System-Specific Reasoning:</strong> Analyzes actual system evidence rather than applying static domain rules.</span>
            </li>
            <li style={{ display: 'flex', gap: '0.75rem', fontSize: '0.95rem' }}>
              <span style={{ color: '#06b6d4', fontWeight: 'bold' }}>✓</span>
              <span><strong>Evidence-Grounded Hypotheses:</strong> Distinguishes observed facts from inferences and unconfirmed hypotheses.</span>
            </li>
            <li style={{ display: 'flex', gap: '0.75rem', fontSize: '0.95rem' }}>
              <span style={{ color: '#06b6d4', fontWeight: 'bold' }}>✓</span>
              <span><strong>Adaptive Multi-Iteration Loop:</strong> Follow-up tests are dynamically generated based on prior observations.</span>
            </li>
            <li style={{ display: 'flex', gap: '0.75rem', fontSize: '0.95rem' }}>
              <span style={{ color: '#06b6d4', fontWeight: 'bold' }}>✓</span>
              <span><strong>Transparent Audit Lineage:</strong> Provides a complete multi-iteration trace of every decision and observation.</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
'''

# 5. New Audit Page
files[os.path.join(frontend_dir, "pages", "NewAuditPage.jsx")] = '''
import React, { useState } from 'react';

const DEMO_PAYLOAD = {
  project_name: "Smart Fraud Detector",
  description: "An AI system that analyzes bank transactions and predicts whether a transaction is fraudulent. It uses transaction amount, location, device information, merchant information and historical account behavior. Transactions with a high fraud probability are automatically blocked.",
  github_url: "",
  documentation: "The system is designed to detect fraudulent financial transactions in real time. It processes transaction information and produces a fraud probability score. If the score exceeds a threshold, the transaction is blocked.",
  sample_inputs: JSON.stringify({
    amount: 5000,
    location: "Hyderabad",
    device: "Android",
    merchant: "Online Store"
  }, null, 2),
  sample_outputs: JSON.stringify({
    fraud_probability: 0.82,
    decision: "BLOCK"
  }, null, 2)
};

export default function NewAuditPage({ onSubmitAudit }) {
  const [formData, setFormData] = useState({
    project_name: "",
    description: "",
    github_url: "",
    documentation: "",
    sample_inputs: "",
    sample_outputs: ""
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleLoadDemo = () => {
    setFormData(DEMO_PAYLOAD);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    let parsedInputs = [];
    let parsedOutputs = [];

    try {
      if (formData.sample_inputs.trim()) {
        parsedInputs = [JSON.parse(formData.sample_inputs)];
      }
    } catch {
      parsedInputs = [formData.sample_inputs];
    }

    try {
      if (formData.sample_outputs.trim()) {
        parsedOutputs = [JSON.parse(formData.sample_outputs)];
      }
    } catch {
      parsedOutputs = [formData.sample_outputs];
    }

    const payload = {
      project: {
        project_name: formData.project_name,
        description: formData.description,
        github_url: formData.github_url || null,
        documentation: formData.documentation || null,
        sample_inputs: parsedInputs,
        sample_outputs: parsedOutputs
      },
      available_tools: ["analysis_tool", "model_tool", "repository_tool"],
      max_iterations: 3
    };

    onSubmitAudit(payload);
  };

  return (
    <div className="new-audit-page">
      <div className="card">
        <div className="card-title">
          <span>Configure New AI System Audit</span>
          <button type="button" className="btn btn-outline" onClick={handleLoadDemo}>
            ⚡ Load Smart Fraud Detector Demo
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label className="form-label">Project Name *</label>
            <input
              type="text"
              name="project_name"
              className="form-control"
              placeholder="e.g. Smart Fraud Detector"
              value={formData.project_name}
              onChange={handleChange}
              required
            />
          </div>

          <div className="form-group">
            <label className="form-label">System Description *</label>
            <textarea
              name="description"
              className="form-control"
              placeholder="Describe what the AI system does, its inputs, outputs, decision process, and affected stakeholders..."
              value={formData.description}
              onChange={handleChange}
              required
            />
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Repository / GitHub URL (Optional)</label>
              <input
                type="text"
                name="github_url"
                className="form-control"
                placeholder="https://github.com/org/repo"
                value={formData.github_url}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Technical Documentation (Optional)</label>
              <input
                type="text"
                name="documentation"
                className="form-control"
                placeholder="Brief technical architecture or operational rules..."
                value={formData.documentation}
                onChange={handleChange}
              />
            </div>
          </div>

          <div className="grid-2">
            <div className="form-group">
              <label className="form-label">Sample Input Payload (JSON / Text)</label>
              <textarea
                name="sample_inputs"
                className="form-control"
                placeholder='{\n  "amount": 5000,\n  "location": "Hyderabad"\n}'
                value={formData.sample_inputs}
                onChange={handleChange}
              />
            </div>

            <div className="form-group">
              <label className="form-label">Sample Output Response (JSON / Text)</label>
              <textarea
                name="sample_outputs"
                className="form-control"
                placeholder='{\n  "fraud_probability": 0.82,\n  "decision": "BLOCK"\n}'
                value={formData.sample_outputs}
                onChange={handleChange}
              />
            </div>
          </div>

          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'flex-end', marginTop: '1.5rem' }}>
            <button type="submit" className="btn btn-primary" style={{ padding: '0.8rem 2.5rem', fontSize: '1rem' }}>
              Launch Adaptive Audit →
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
'''

# 6. Audit Results Page
files[os.path.join(frontend_dir, "pages", "AuditResultsPage.jsx")] = '''
import React from 'react';

export default function AuditResultsPage({ auditData, isLoading, error, onBack }) {
  if (isLoading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔄</div>
        <h2 style={{ fontSize: '1.5rem', color: '#fff', marginBottom: '0.5rem' }}>Running Adaptive AI System Audit...</h2>
        <p style={{ color: '#94a3b8', maxWidth: '600px', margin: '0 auto 1.5rem' }}>
          Extracting System Profile → Generating Grounded Hypotheses → Executing Controlled Tool Probes → Reasoning Adaptive Follow-ups
        </p>
        <div style={{ display: 'inline-block', padding: '0.5rem 1rem', background: '#131b29', borderRadius: '6px', border: '1px solid #06b6d4', color: '#06b6d4', fontSize: '0.85rem' }}>
          Evaluating multi-iteration evidence trace...
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card" style={{ borderColor: '#ef4444' }}>
        <div className="card-title" style={{ color: '#f87171' }}>Audit Failure</div>
        <p style={{ color: '#cbd5e1', marginBottom: '1rem' }}>{error}</p>
        <button className="btn btn-secondary" onClick={onBack}>← Back to Form</button>
      </div>
    );
  }

  if (!auditData) return null;

  const { audit_id, system_profile, hypotheses, investigation_trace, final_evidence, unresolved_questions, limitations, status } = auditData;

  return (
    <div className="audit-results-page">
      {/* Header Summary Bar */}
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>Audit Session ID</div>
          <h2 style={{ fontSize: '1.4rem', color: '#fff', fontWeight: '800' }}>{audit_id}</h2>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span className="badge badge-status">Status: {status}</span>
          <button className="btn btn-secondary" onClick={onBack}>New Audit</button>
        </div>
      </div>

      {/* Adaptive Flow Visual Diagram */}
      <div className="card">
        <div className="card-title">Adaptive Investigation Flow Diagram</div>
        <div className="flow-bar">
          <div className="flow-node active">SYSTEM PROHIBIT</div>
          <div className="flow-arrow">→</div>
          <div className="flow-node active">SYSTEM PROFILE</div>
          <div className="flow-arrow">→</div>
          <div className="flow-node active">HYPOTHESES ({hypotheses ? hypotheses.length : 0})</div>
          
          {investigation_trace && investigation_trace.map((iter, idx) => (
            <React.Fragment key={idx}>
              <div className="flow-arrow">→</div>
              <div className="flow-node active">
                ITERATION {iter.iteration}: {iter.investigation_plan ? iter.investigation_plan.investigation_goal.substring(0, 25) : 'Probe'}...
              </div>
              <div className="flow-arrow">→</div>
              <div className="flow-node active">
                DECISION: {iter.adaptive_decision ? iter.adaptive_decision.action.toUpperCase() : 'NEXT'}
              </div>
            </React.Fragment>
          ))}
          <div className="flow-arrow">→</div>
          <div className="flow-node active" style={{ borderColor: '#10b981', color: '#34d399' }}>AUDIT TRACE COMPLETE</div>
        </div>
      </div>

      {/* System Profile Section */}
      <div className="card">
        <div className="card-title">
          <span>System Profile</span>
          <span className="badge badge-observed">Phase 1 Grounded Model</span>
        </div>
        <div className="grid-3">
          <div className="kv-pair">
            <div className="kv-label"><span className="badge badge-observed">OBSERVED</span> Purpose</div>
            <div className="kv-value">{system_profile.purpose || 'Unknown'}</div>
          </div>
          <div className="kv-pair">
            <div className="kv-label"><span className="badge badge-observed">OBSERVED</span> Intended Use</div>
            <div className="kv-value">{system_profile.intended_use || 'Unknown'}</div>
          </div>
          <div className="kv-pair">
            <div className="kv-label"><span className="badge badge-inferred">INFERRED</span> AI System Type</div>
            <div className="kv-value">{system_profile.ai_system_type || 'Unknown'}</div>
          </div>
          <div className="kv-pair">
            <div className="kv-label"><span className="badge badge-observed">OBSERVED</span> Inputs</div>
            <div className="kv-value">{Array.isArray(system_profile.inputs) ? system_profile.inputs.join(', ') : 'Unknown'}</div>
          </div>
          <div className="kv-pair">
            <div className="kv-label"><span className="badge badge-observed">OBSERVED</span> Outputs</div>
            <div className="kv-value">{Array.isArray(system_profile.outputs) ? system_profile.outputs.join(', ') : 'Unknown'}</div>
          </div>
          <div className="kv-pair">
            <div className="kv-label"><span className="badge badge-inferred">INFERRED</span> Autonomy Level</div>
            <div className="kv-value">{system_profile.autonomy_level || 'Unknown'}</div>
          </div>
          <div className="kv-pair">
            <div className="kv-label"><span className="badge badge-observed">OBSERVED</span> Human Involvement</div>
            <div className="kv-value">{system_profile.human_involvement || 'Unknown'}</div>
          </div>
          <div className="kv-pair">
            <div className="kv-label"><span className="badge badge-unknown">UNKNOWN</span> Sensitive Data</div>
            <div className="kv-value">{Array.isArray(system_profile.sensitive_data) && system_profile.sensitive_data.length > 0 ? system_profile.sensitive_data.join(', ') : 'None Specified'}</div>
          </div>
          <div className="kv-pair">
            <div className="kv-label"><span className="badge badge-unknown">UNKNOWN</span> Important Unknowns</div>
            <div className="kv-value">{Array.isArray(system_profile.important_unknowns) && system_profile.important_unknowns.length > 0 ? system_profile.important_unknowns.join('; ') : 'None'}</div>
          </div>
        </div>
      </div>

      {/* Hypotheses Section */}
      <div className="card">
        <div className="card-title">
          <span>Hypotheses Under Investigation</span>
          <span style={{ fontSize: '0.8rem', color: '#94a3b8', fontWeight: 'normal' }}>Grounded in System Profile evidence (Not confirmed findings)</span>
        </div>
        {hypotheses && hypotheses.length > 0 ? (
          hypotheses.map((hyp, idx) => (
            <div key={idx} className="step-box" style={{ marginBottom: '1rem' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                <span style={{ fontWeight: '700', color: '#06b6d4' }}>[{hyp.id}] {hyp.hypothesis}</span>
                <div>
                  <span className={`badge badge-${hyp.priority}`} style={{ marginRight: '0.5rem' }}>{hyp.priority} Priority</span>
                  <span className="badge badge-observed">Confidence: {(hyp.confidence * 100).toFixed(0)}%</span>
                </div>
              </div>
              <p style={{ fontSize: '0.9rem', color: '#cbd5e1', marginBottom: '0.4rem' }}><strong>Why Plausible:</strong> {hyp.why_it_is_plausible}</p>
              <p style={{ fontSize: '0.85rem', color: '#94a3b8' }}><strong>Affected Part:</strong> {hyp.affected_part} | <strong>Potential Consequence:</strong> {hyp.potential_consequence}</p>
            </div>
          ))
        ) : (
          <p style={{ color: '#94a3b8' }}>No hypotheses could be justified based on available evidence.</p>
        )}
      </div>

      {/* Adaptive Investigation Trace */}
      <div className="card">
        <div className="card-title">
          <span>Adaptive Investigation Trace</span>
          <span className="badge badge-observed">Evidence-Driven Multi-Iteration Lineage</span>
        </div>

        {investigation_trace && investigation_trace.map((iter, idx) => (
          <div key={idx} className="card iteration-card">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.75rem', borderBottom: '1px solid #26354a', paddingBottom: '0.5rem' }}>
              <h3 style={{ fontSize: '1.1rem', color: '#fff' }}>Iteration {iter.iteration}</h3>
              <span className={`badge ${iter.adaptive_decision.action === 'continue' ? 'badge-medium' : 'badge-low'}`}>
                Adaptive Action: {iter.adaptive_decision.action.toUpperCase()}
              </span>
            </div>

            <div style={{ marginBottom: '0.8rem' }}>
              <strong style={{ color: '#38bdf8', fontSize: '0.9rem' }}>Investigation Goal:</strong>
              <p style={{ color: '#cbd5e1', fontSize: '0.95rem' }}>{iter.investigation_plan.investigation_goal}</p>
            </div>

            {/* Steps executed */}
            <div style={{ marginBottom: '1rem' }}>
              <strong style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Tool Executions ({iter.tool_executions.length}):</strong>
              {iter.tool_executions.map((step, sIdx) => (
                <div key={sIdx} className="step-box">
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.85rem', marginBottom: '0.3rem' }}>
                    <span style={{ color: '#a7f3d0', fontWeight: '600' }}>Step {step.step_id} - Tool: {step.tool}</span>
                    <span style={{ color: step.status === 'success' ? '#34d399' : '#fbbf24' }}>Status: {step.status}</span>
                  </div>
                  <pre style={{ background: '#0b0f17', padding: '0.5rem', borderRadius: '4px', fontSize: '0.8rem', color: '#94a3b8', overflowX: 'auto' }}>
                    {JSON.stringify(step.parameters, null, 2)}
                  </pre>
                </div>
              ))}
            </div>

            {/* Observations */}
            <div style={{ marginBottom: '1rem' }}>
              <strong style={{ color: '#94a3b8', fontSize: '0.85rem' }}>Derived Observations:</strong>
              {iter.observations.map((obs, oIdx) => (
                <div key={oIdx} style={{ fontSize: '0.9rem', color: '#cbd5e1', padding: '0.4rem 0.8rem', background: '#131b29', borderRadius: '4px', marginTop: '0.3rem' }}>
                  • {obs.description} <span style={{ color: '#64748b', fontSize: '0.8rem' }}>({obs.source})</span>
                </div>
              ))}
            </div>

            {/* Adaptive Decision Reasoning */}
            <div className="step-box" style={{ borderColor: '#06b6d4', background: 'rgba(6, 182, 212, 0.05)' }}>
              <div style={{ fontWeight: '700', color: '#06b6d4', fontSize: '0.9rem', marginBottom: '0.3rem' }}>
                Why did the agent decide to {iter.adaptive_decision.action.toUpperCase()}?
              </div>
              <p style={{ fontSize: '0.9rem', color: '#f1f5f9', marginBottom: '0.5rem' }}>{iter.adaptive_decision.reasoning}</p>
              
              {iter.adaptive_decision.next_question && (
                <div style={{ marginTop: '0.5rem', padding: '0.4rem 0.6rem', background: 'rgba(59, 130, 246, 0.15)', borderRadius: '4px', borderLeft: '3px solid #3b82f6' }}>
                  <strong style={{ color: '#60a5fa', fontSize: '0.85rem' }}>Target Next Question for Follow-up Iteration:</strong>
                  <p style={{ color: '#fff', fontSize: '0.9rem', fontWeight: '600' }}>"{iter.adaptive_decision.next_question}"</p>
                </div>
              )}
            </div>
          </div>
        ))}
      </div>

      {/* Evidence & Limitations */}
      <div className="grid-2">
        <div className="card">
          <div className="card-title">Aggregated Evidence Log</div>
          <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
            {final_evidence && final_evidence.length > 0 ? (
              final_evidence.map((ev, idx) => (
                <li key={idx} style={{ fontSize: '0.85rem', color: '#cbd5e1', background: '#131b29', padding: '0.5rem 0.75rem', borderRadius: '4px' }}>
                  🔍 {ev}
                </li>
              ))
            ) : (
              <li style={{ color: '#94a3b8', fontSize: '0.9rem' }}>No evidence items recorded.</li>
            )}
          </ul>
        </div>

        <div className="card">
          <div className="card-title">Limitations & Unresolved Questions</div>
          <div style={{ marginBottom: '1rem' }}>
            <strong style={{ color: '#fbbf24', fontSize: '0.85rem' }}>Known Limitations:</strong>
            {limitations && limitations.length > 0 ? (
              limitations.map((lim, idx) => (
                <div key={idx} style={{ fontSize: '0.85rem', color: '#cbd5e1', marginTop: '0.2rem' }}>⚠️ {lim}</div>
              ))
            ) : (
              <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>None reported.</div>
            )}
          </div>

          <div>
            <strong style={{ color: '#60a5fa', fontSize: '0.85rem' }}>Unresolved Questions:</strong>
            {unresolved_questions && unresolved_questions.length > 0 ? (
              unresolved_questions.map((uq, idx) => (
                <div key={idx} style={{ fontSize: '0.85rem', color: '#cbd5e1', marginTop: '0.2rem' }}>❓ {uq}</div>
              ))
            ) : (
              <div style={{ fontSize: '0.85rem', color: '#94a3b8' }}>All key questions resolved.</div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
'''

# 7. App.jsx
files[os.path.join(frontend_dir, "App.jsx")] = '''
import React, { useState } from 'react';
import Header from './components/Header';
import LandingPage from './pages/LandingPage';
import NewAuditPage from './pages/NewAuditPage';
import AuditResultsPage from './pages/AuditResultsPage';
import { runAudit } from './services/api';
import './styles/dashboard.css';

export default function App() {
  const [currentRoute, setCurrentRoute] = useState('/');
  const [auditData, setAuditData] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleNavigate = (route) => {
    setCurrentRoute(route);
  };

  const handleStartAudit = async (payload) => {
    setCurrentRoute('/audit/results');
    setIsLoading(true);
    setError(null);
    try {
      const result = await runAudit(payload);
      setAuditData(result);
    } catch (err) {
      setError(err.message || "Failed to execute audit");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="app-container">
      <Header currentRoute={currentRoute} onNavigate={handleNavigate} />
      <main className="content-wrapper">
        {currentRoute === '/' && <LandingPage onNavigate={handleNavigate} />}
        {currentRoute === '/audit/new' && <NewAuditPage onSubmitAudit={handleStartAudit} />}
        {currentRoute === '/audit/results' && (
          <AuditResultsPage
            auditData={auditData}
            isLoading={isLoading}
            error={error}
            onBack={() => setCurrentRoute('/audit/new')}
          />
        )}
      </main>
      <footer className="footer">
        AI Risk Manager • Adaptive Ethical Auditor for AI Systems • Hackathon Prototype
      </footer>
    </div>
  );
}
'''

for path, content in files.items():
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content.strip())
    print(f"Successfully wrote {path}")

print("All frontend files created successfully.")
