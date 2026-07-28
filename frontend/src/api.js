const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "";

export async function uploadSrt(
  file,
  batchSize
) {
  const formData = new FormData();

  formData.append(
    "file",
    file
  );

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
      data.detail ||
      "Failed to upload SRT file."
    );
  }

  return data;
}


export async function getJobStatus(
  jobId
) {
  const response = await fetch(
    `${API_BASE_URL}/api/jobs/${jobId}`
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(
      data.detail ||
      "Failed to get job status."
    );
  }

  return data;
}


export function getDownloadUrl(
  jobId
) {
  return (
    `${API_BASE_URL}/api/jobs/${jobId}/download`
  );
}
