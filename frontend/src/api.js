const API_BASE_URL =
  "https://ultimate-ai-translator-v2.onrender.com";

export async function uploadSrt(file, batchSize) {
  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/api/upload?batch_size=${batchSize}`,
    {
      method: "POST",
      body: formData,
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Upload failed."
    );
  }

  return data;
}

export async function getJobStatus(jobId) {
  const response = await fetch(
    `${API_BASE_URL}/api/jobs/${jobId}`
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail || "Status failed."
    );
  }

  return data;
}

export function getDownloadUrl(jobId) {
  return `${API_BASE_URL}/api/jobs/${jobId}/download`;
}
