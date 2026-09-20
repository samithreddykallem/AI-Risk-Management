import React, { useState } from 'react';

export default function AuditResultsPage({ auditData, isLoading, error, onBack }) {
  const [showDeveloperDetails, setShowDeveloperDetails] = useState(false);

  if (isLoading) {
    return (
      <div className="card" style={{ textAlign: 'center', padding: '4rem 2rem' }}>
        <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🔄</div>
        <h2 style={{ fontSize: '1.5rem', color: '#fff', marginBottom: '0.5rem' }}>Running Adaptive AI System Audit...</h2>
        <p style={{ color: '#94a3b8', maxWidth: '600px', margin: '0 auto 1.5rem' }}>
          Analyzing AI System → Forming Hypotheses → Executing Controlled Tests → Reasoning Adaptive Decisions
        </p>
        <div style={{ display: 'inline-block', padding: '0.5rem 1rem', background: '#131b29', borderRadius: '6px', border: '1px solid #06b6d4', color: '#06b6d4', fontSize: '0.85rem' }}>
          Generating Human-Readable Audit Report...
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

  const { audit_id, system_profile, hypotheses, investigation_trace, status } = auditData;

  // Extract key elements safely from audit state
  const primaryHypothesis = (hypotheses && hypotheses.length > 0) ? hypotheses[0] : null;
  const primaryIteration = (investigation_trace && investigation_trace.length > 0) ? investigation_trace[0] : null;
  const toolExecs = primaryIteration?.tool_executions || [];
  const adaptiveDecision = primaryIteration?.adaptive_decision || { action: 'stop', reasoning: 'Evidence collected was sufficient to address hypothesis.' };

  // Helper to extract baseline input vs perturbations
  let baseInput = {};
  let perturbations = {};
  let perturbedFields = [];

  toolExecs.forEach(exec => {
    if (exec.parameters) {
      if (exec.parameters.base_input) baseInput = { ...baseInput, ...exec.parameters.base_input };
      if (exec.parameters.original_input) baseInput = { ...baseInput, ...exec.parameters.original_input };
      if (exec.parameters.perturbations) perturbations = { ...perturbations, ...exec.parameters.perturbations };
      if (exec.parameters.modified_input) perturbations = { ...perturbations, ...exec.parameters.modified_input };
      if (exec.parameters.perturbed_fields) perturbedFields = exec.parameters.perturbed_fields;
    }
  });

  // Calculate changed vs unchanged attributes
  const changedVars = [];
  const unchangedVars = [];

  Object.entries(baseInput).forEach(([key, val]) => {
    const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
    if (perturbations.hasOwnProperty(key)) {
      changedVars.push({ name: formattedKey, key, before: val, after: perturbations[key] });
    } else if (perturbedFields.includes(key)) {
      changedVars.push({ name: formattedKey, key, before: val, after: 'Modified' });
    } else {
      unchangedVars.push({ name: formattedKey, key, val });
    }
  });

  Object.entries(perturbations).forEach(([key, val]) => {
    if (!baseInput.hasOwnProperty(key)) {
      const formattedKey = key.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase());
      changedVars.push({ name: formattedKey, key, before: 'Standard', after: val });
    }
  });

  // Check for model output score / decision changes in tool outputs
  let beforeScore = null;
  let afterScore = null;
  let beforeDecision = null;
  let afterDecision = null;

  toolExecs.forEach(exec => {
    if (exec.result) {
      if (exec.result.output_a && typeof exec.result.output_a === 'object') {
        if (exec.result.output_a.risk_score !== undefined) beforeScore = exec.result.output_a.risk_score;
        if (exec.result.output_a.decision !== undefined) beforeDecision = exec.result.output_a.decision;
        if (exec.result.output_a.recommendation !== undefined) beforeDecision = exec.result.output_a.recommendation;
      }
      if (exec.result.output_b && typeof exec.result.output_b === 'object') {
        if (exec.result.output_b.risk_score !== undefined) afterScore = exec.result.output_b.risk_score;
        if (exec.result.output_b.decision !== undefined) afterDecision = exec.result.output_b.decision;
        if (exec.result.output_b.recommendation !== undefined) afterDecision = exec.result.output_b.recommendation;
      }
    }
  });

  const hasScoreChange = (beforeScore !== null && afterScore !== null && beforeScore !== afterScore);
  const hasDecisionChange = (beforeDecision !== null && afterDecision !== null && beforeDecision !== afterDecision);
  const hasOutputChangeDetails = hasScoreChange || hasDecisionChange;

  const targetVariable = changedVars.length > 0 ? changedVars[0].name : 'Input Parameter';
  const targetVarShort = changedVars.length > 0 ? changedVars[0].name : 'input attribute';

  return (
    <div className="audit-results-page" style={{ maxWidth: '900px', margin: '0 auto' }}>
      
      {/* Header Bar */}
      <div className="card" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: '0.8rem', color: '#94a3b8', textTransform: 'uppercase', letterSpacing: '0.5px' }}>AI Audit Session</div>
          <h2 style={{ fontSize: '1.4rem', color: '#fff', fontWeight: '800' }}>{system_profile.purpose ? system_profile.purpose.split('.')[0] : audit_id}</h2>
        </div>
        <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
          <span className="badge badge-status">Status: {status || 'Complete'}</span>
          <button className="btn btn-secondary" onClick={onBack}>← Start New Audit</button>
        </div>
      </div>

      {/* Visual Flow Timeline Bar */}
      <div className="card">
        <div className="card-title">Audit Lineage Timeline</div>
        <div className="flow-bar">
          <div className="flow-node active">1. SYSTEM UNDERSTANDING</div>
          <div className="flow-arrow">→</div>
          <div className="flow-node active">2. HYPOTHESIS IDENTIFIED</div>
          <div className="flow-arrow">→</div>
          <div className="flow-node active">3. CONTROLLED TEST</div>
          <div className="flow-arrow">→</div>
          <div className="flow-node active">4. OBSERVATION</div>
          <div className="flow-arrow">→</div>
          <div className={`flow-node active ${adaptiveDecision.action === 'stop' ? 'flow-node-stop' : 'flow-node-continue'}`}>
            5. {adaptiveDecision.action === 'stop' ? 'DECISION: STOP' : 'DECISION: CONTINUE'}
          </div>
        </div>
      </div>

      {/* SECTION 1: WHAT THE AI DOES */}
      <div className="card">
        <div className="card-title">
          <span>1. What the AI does</span>
          <span className="badge badge-observed">System Purpose</span>
        </div>
        <h3 style={{ color: '#06b6d4', fontSize: '1.1rem', marginBottom: '0.4rem', fontWeight: '700' }}>
          {system_profile.intended_use || system_profile.purpose || 'AI System Model Execution'}
        </h3>
        <p style={{ color: '#cbd5e1', fontSize: '1rem', lineHeight: '1.6' }}>
          "{system_profile.purpose || 'The system analyzes input information to assist in automated recommendations.'}"
        </p>
      </div>

      {/* SECTION 2: WHAT DID THE AUDITOR IDENTIFY */}
      <div className="card">
        <div className="card-title">
          <span>2. What did the auditor identify?</span>
          <span className="badge badge-medium">Potential Risk Identified</span>
        </div>
        <h3 style={{ color: '#38bdf8', fontSize: '1.1rem', marginBottom: '0.4rem', fontWeight: '700' }}>
          Potential {targetVariable} Influence
        </h3>
        <p style={{ color: '#cbd5e1', fontSize: '0.95rem', marginBottom: '1rem' }}>
          "The auditor identified {targetVarShort} as an input that may influence the system's output."
        </p>
        
        <div style={{ background: '#0f172a', padding: '1rem', borderRadius: '6px', borderLeft: '3px solid #3b82f6' }}>
          <strong style={{ color: '#60a5fa', fontSize: '0.85rem', textTransform: 'uppercase' }}>Question being investigated:</strong>
          <p style={{ color: '#fff', fontSize: '0.95rem', fontWeight: '600', marginTop: '0.3rem' }}>
            "{primaryHypothesis?.hypothesis || `Could changing the ${targetVarShort} affect the AI's output when other information stays the same?`}"
          </p>
        </div>
      </div>

      {/* SECTION 3: WHAT DID THE AUDITOR TEST */}
      <div className="card">
        <div className="card-title">
          <span>3. What did the auditor test?</span>
          <span className="badge badge-status">Controlled Test Comparison</span>
        </div>

        <div className="grid-2" style={{ gap: '1rem', marginBottom: '1.25rem' }}>
          {/* Original Applicant */}
          <div style={{ background: '#131b29', padding: '1rem', borderRadius: '8px', borderLeft: '3px solid #3b82f6' }}>
            <h4 style={{ color: '#60a5fa', fontSize: '0.85rem', textTransform: 'uppercase', fontWeight: '700', marginBottom: '0.75rem' }}>
              ORIGINAL APPLICANT (Baseline Input)
            </h4>
            {Object.keys(baseInput).length > 0 ? (
              Object.entries(baseInput).map(([k, v]) => (
                <div key={k} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.25rem 0', fontSize: '0.9rem', color: '#cbd5e1' }}>
                  <span style={{ color: '#94a3b8' }}>{k.replace(/_/g, ' ')}:</span>
                  <strong style={{ color: '#fff' }}>{typeof v === 'object' ? JSON.stringify(v) : String(v)}</strong>
                </div>
              ))
            ) : (
              <p style={{ color: '#94a3b8', fontSize: '0.9rem' }}>Baseline parameters evaluated.</p>
            )}
          </div>

          {/* Modified Applicant */}
          <div style={{ background: '#131b29', padding: '1rem', borderRadius: '8px', borderLeft: '3px solid #f59e0b' }}>
            <h4 style={{ color: '#fbbf24', fontSize: '0.85rem', textTransform: 'uppercase', fontWeight: '700', marginBottom: '0.75rem' }}>
              MODIFIED APPLICANT (Perturbed Test Input)
            </h4>
            {changedVars.map((item) => (
              <div key={item.key} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.25rem 0', fontSize: '0.9rem', color: '#cbd5e1' }}>
                <span style={{ color: '#fbbf24' }}>{item.name}:</span>
                <strong style={{ color: '#fef08a' }}>{typeof item.after === 'object' ? JSON.stringify(item.after) : String(item.after)}</strong>
              </div>
            ))}
            {unchangedVars.map((item) => (
              <div key={item.key} style={{ display: 'flex', justifyContent: 'space-between', padding: '0.25rem 0', fontSize: '0.9rem', color: '#cbd5e1' }}>
                <span style={{ color: '#94a3b8' }}>{item.name}:</span>
                <strong style={{ color: '#fff' }}>{typeof item.val === 'object' ? JSON.stringify(item.val) : String(item.val)}</strong>
              </div>
            ))}
          </div>
        </div>

        {/* Explicit Change Summary */}
        <div style={{ background: '#0b0f17', padding: '0.8rem 1rem', borderRadius: '6px', display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
          <div>
            <strong style={{ color: '#f87171', fontSize: '0.85rem', textTransform: 'uppercase' }}>What changed?</strong>
            {changedVars.length > 0 ? (
              changedVars.map((item) => (
                <div key={item.key} style={{ color: '#cbd5e1', fontSize: '0.9rem', marginTop: '0.2rem' }}>
                  {item.name}: <span style={{ textDecoration: 'line-through', color: '#94a3b8' }}>{String(item.before)}</span> → <strong style={{ color: '#fef08a' }}>{String(item.after)}</strong>
                </div>
              ))
            ) : (
              <div style={{ color: '#cbd5e1', fontSize: '0.9rem', marginTop: '0.2rem' }}>Controlled input variable modified.</div>
            )}
          </div>

          <div>
            <strong style={{ color: '#34d399', fontSize: '0.85rem', textTransform: 'uppercase' }}>What stayed the same?</strong>
            <div style={{ color: '#cbd5e1', fontSize: '0.9rem', marginTop: '0.2rem' }}>
              {unchangedVars.length > 0 
                ? unchangedVars.map(u => `${u.name}: ${String(u.val)}`).join(', ') 
                : 'All baseline parameters remained constant.'}
            </div>
          </div>
        </div>
      </div>

      {/* SECTION 4: WHAT HAPPENED */}
      <div className="card">
        <div className="card-title">
          <span>4. What happened?</span>
          <span className="badge badge-observed">Observation</span>
        </div>
        <p style={{ color: '#f1f5f9', fontSize: '1.05rem', fontWeight: '500', lineHeight: '1.5' }}>
          {hasOutputChangeDetails
            ? `The AI produced a different output after the ${targetVarShort} was changed, while the other tested attributes remained the same.`
            : `The ${targetVarShort} was successfully changed for the controlled test, but the available evidence does not show a change in the model's actual decision or risk score.`}
        </p>
      </div>

      {/* SECTION 5: SHOW HOW THE OUTPUT CHANGED */}
      <div className="card">
        <div className="card-title">
          <span>5. Show HOW the output changed</span>
          <span className="badge badge-observed">Output Impact Analysis</span>
        </div>

        {hasOutputChangeDetails ? (
          <div>
            <div className="grid-2" style={{ gap: '1rem', marginBottom: '1rem' }}>
              <div style={{ background: '#131b29', padding: '0.8rem 1rem', borderRadius: '6px' }}>
                <strong style={{ color: '#94a3b8', fontSize: '0.8rem', textTransform: 'uppercase' }}>Before the change</strong>
                {beforeScore !== null && <div style={{ color: '#fff', fontSize: '0.95rem', marginTop: '0.2rem' }}>Risk Score: <strong>{beforeScore}</strong></div>}
                {beforeDecision !== null && <div style={{ color: '#fff', fontSize: '0.95rem' }}>Decision: <strong>{beforeDecision}</strong></div>}
              </div>

              <div style={{ background: '#131b29', padding: '0.8rem 1rem', borderRadius: '6px' }}>
                <strong style={{ color: '#94a3b8', fontSize: '0.8rem', textTransform: 'uppercase' }}>After the change</strong>
                {afterScore !== null && <div style={{ color: '#fff', fontSize: '0.95rem', marginTop: '0.2rem' }}>Risk Score: <strong>{afterScore}</strong></div>}
                {afterDecision !== null && <div style={{ color: '#fff', fontSize: '0.95rem' }}>Decision: <strong>{afterDecision}</strong></div>}
              </div>
            </div>

            <div style={{ background: '#0b0f17', padding: '0.8rem 1rem', borderRadius: '6px', marginBottom: '0.8rem' }}>
              <strong style={{ color: '#06b6d4', fontSize: '0.85rem', textTransform: 'uppercase' }}>Change observed:</strong>
              {hasScoreChange && <div style={{ color: '#cbd5e1', fontSize: '0.9rem' }}>Risk Score: {beforeScore} → <strong style={{ color: '#38bdf8' }}>{afterScore}</strong></div>}
              {hasDecisionChange && <div style={{ color: '#cbd5e1', fontSize: '0.9rem' }}>Decision: {beforeDecision} → <strong style={{ color: '#38bdf8' }}>{afterDecision}</strong></div>}
            </div>

            <p style={{ color: '#cbd5e1', fontSize: '0.9rem', fontStyle: 'italic' }}>
              "Only the {targetVarShort} was changed, so this difference indicates that {targetVarShort} may have influenced the model's output."
            </p>
          </div>
        ) : (
          <div style={{ background: '#131b29', padding: '1rem', borderRadius: '6px' }}>
            <p style={{ color: '#cbd5e1', fontSize: '0.95rem', lineHeight: '1.5' }}>
              "An output difference was observed, but the available audit data does not contain enough information to show how the risk score or approval decision changed."
            </p>
          </div>
        )}
      </div>

      {/* SECTION 6: WHAT DOES THIS MEAN */}
      <div className="card">
        <div className="card-title">
          <span>6. What does this mean?</span>
          <span className="badge badge-status">Evidence Context</span>
        </div>
        <p style={{ color: '#e2e8f0', fontSize: '0.95rem', lineHeight: '1.6' }}>
          "This test provides evidence that the changed input may influence the AI system's output. However, one test is not enough to determine whether the behavior is consistent across applicants."
        </p>
      </div>

      {/* SECTION 7: AUDITOR DECISION */}
      <div className="card" style={{ 
        background: adaptiveDecision.action === 'stop' ? 'rgba(16, 185, 129, 0.08)' : 'rgba(245, 158, 11, 0.08)', 
        border: `1px solid ${adaptiveDecision.action === 'stop' ? '#10b981' : '#f59e0b'}` 
      }}>
        <div className="card-title" style={{ borderBottomColor: adaptiveDecision.action === 'stop' ? 'rgba(16, 185, 129, 0.2)' : 'rgba(245, 158, 11, 0.2)' }}>
          <span>7. Auditor Decision</span>
          <span className="badge badge-status">Adaptive Action</span>
        </div>

        <h3 style={{ 
          fontSize: '1.2rem', 
          color: adaptiveDecision.action === 'stop' ? '#34d399' : '#fbbf24', 
          fontWeight: '800', 
          marginBottom: '0.4rem' 
        }}>
          {adaptiveDecision.action === 'stop' ? '🛑 Investigation Stopped' : '➡️ Investigation Continues'}
        </h3>

        <p style={{ color: '#f8fafc', fontSize: '0.95rem', fontWeight: '500' }}>
          "{adaptiveDecision.action === 'stop' 
            ? 'The auditor stopped because the evidence collected was sufficient to address the current hypothesis.' 
            : 'The auditor determined that more evidence is needed and selected the next investigation based on the previous observation.'}"
        </p>
        
        <p style={{ color: '#94a3b8', fontSize: '0.85rem', marginTop: '0.4rem' }}>
          Reasoning: {adaptiveDecision.reasoning}
        </p>
      </div>

      {/* SECTION 8: FINAL SUMMARY */}
      <div className="card">
        <div className="card-title">
          <span>8. Final Summary</span>
          <span className="badge badge-observed">Audit Overview</span>
        </div>

        <p style={{ color: '#cbd5e1', fontSize: '0.95rem', marginBottom: '1rem', lineHeight: '1.5' }}>
          "An AI auditor examined the system, identified a potential risk, performed a controlled test, observed the result, and decided whether further investigation was necessary."
        </p>

        <div style={{ background: '#0f172a', padding: '1rem', borderRadius: '6px', border: '1px solid #1e293b' }}>
          <div style={{ fontSize: '0.9rem', color: '#cbd5e1', marginBottom: '0.3rem' }}>
            <strong style={{ color: '#60a5fa' }}>Hypothesis:</strong> {primaryHypothesis?.hypothesis || `Potential ${targetVarShort} influence`}
          </div>
          <div style={{ fontSize: '0.9rem', color: '#cbd5e1', marginBottom: '0.3rem' }}>
            <strong style={{ color: '#fbbf24' }}>Test:</strong> {changedVars.length > 0 ? `${changedVars[0].name} changed from ${changedVars[0].before} to ${changedVars[0].after}` : 'Controlled perturbation applied'}
          </div>
          <div style={{ fontSize: '0.9rem', color: '#cbd5e1', marginBottom: '0.3rem' }}>
            <strong style={{ color: '#34d399' }}>Observation:</strong> {hasOutputChangeDetails ? 'Output difference observed' : 'Input changed; output difference not explicitly confirmed'}
          </div>
          <div style={{ fontSize: '0.9rem', color: '#cbd5e1' }}>
            <strong style={{ color: adaptiveDecision.action === 'stop' ? '#34d399' : '#fbbf24' }}>Decision:</strong> {adaptiveDecision.action === 'stop' ? 'STOP' : 'CONTINUE'}
          </div>
        </div>
      </div>

      {/* Developer Details (Collapsible Debug Mode) */}
      <div className="card" style={{ background: '#0b0f17', borderColor: '#1e293b' }}>
        <button
          className="btn btn-secondary"
          style={{ width: '100%', textAlign: 'left', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
          onClick={() => setShowDeveloperDetails(!showDeveloperDetails)}
        >
          <span>🛠️ Developer Details (Raw Audit Payload & Tool Logs)</span>
          <span>{showDeveloperDetails ? '▲ Collapse' : '▼ Expand'}</span>
        </button>

        {showDeveloperDetails && (
          <div style={{ marginTop: '1rem', paddingTop: '1rem', borderTop: '1px solid #1e293b' }}>
            <h4 style={{ color: '#06b6d4', fontSize: '0.9rem', marginBottom: '0.5rem' }}>Raw Audit Response JSON:</h4>
            <pre style={{ background: '#070a0f', padding: '1rem', borderRadius: '6px', fontSize: '0.8rem', color: '#38bdf8', overflowX: 'auto', maxHeight: '400px' }}>
              {JSON.stringify(auditData, null, 2)}
            </pre>
          </div>
        )}
      </div>

    </div>
  );
}
