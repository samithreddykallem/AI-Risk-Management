const BASE_URL = (import.meta.env.VITE_API_URL || "http://127.0.0.1:8000").replace(/\/+$/, "");

export async function uploadDataset(file) {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch(`${BASE_URL}/engine/upload-dataset`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Dataset Upload Failed (${response.status}): ${errText}`);
  }

  return await response.json();
}

export async function profileDataset(datasetPath, datasetName, targetColumn) {
  const formData = new FormData();
  formData.append("dataset_path", datasetPath);
  if (datasetName) formData.append("dataset_name", datasetName);
  if (targetColumn) formData.append("target_column", targetColumn);

  const response = await fetch(`${BASE_URL}/engine/profile-dataset`, {
    method: "POST",
    body: formData
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Dataset Profiling Failed (${response.status}): ${errText}`);
  }

  return await response.json();
}

export async function runAudit(auditPayload) {
  const response = await fetch(`${BASE_URL}/engine/audit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify(auditPayload)
  });

  if (!response.ok) {
    const errText = await response.text();
    throw new Error(`Adaptive Audit Failed (${response.status}): ${errText}`);
  }

  return await response.json();
}

export async function checkHealth() {
  try {
    const res = await fetch(`${BASE_URL}/health`);
    return res.ok;
  } catch {
    return false;
  }
}
