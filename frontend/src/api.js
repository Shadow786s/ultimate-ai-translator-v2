const API_BASE_URL =
  "https://ultimate-ai-translator-v2.onrender.com";


async function parseResponse(response, fallbackMessage) {
  let data = {};

  try {
    data = await response.json();
  } catch {
    data = {};
  }

  if (!response.ok) {
    throw new Error(
      data.detail ||
      data.message ||
      fallbackMessage
    );
  }

  return data;
}


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

  return await parseResponse(
    response,
    "Upload failed."
  );
}


export async function getJobStatus(
  jobId
) {
  const response = await fetch(
    `${API_BASE_URL}/api/jobs/${jobId}`,
    {
      method: "GET",
      cache: "no-store",
    }
  );

  return await parseResponse(
    response,
    "Unable to get job status."
  );
}


export function getDownloadUrl(
  jobId
) {
  return (
    `${API_BASE_URL}/api/jobs/${jobId}/download`
  );
}


export async function cancelJob(
  jobId
) {
  const response = await fetch(
    `${API_BASE_URL}/api/jobs/${jobId}/cancel`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  return await parseResponse(
    response,
    "Unable to cancel translation job."
  );
}


export async function pauseJob(
  jobId
) {
  const response = await fetch(
    `${API_BASE_URL}/api/jobs/${jobId}/pause`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  return await parseResponse(
    response,
    "Unable to pause translation job."
  );
}


export async function resumeJob(
  jobId
) {
  const response = await fetch(
    `${API_BASE_URL}/api/jobs/${jobId}/resume`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
    }
  );

  return await parseResponse(
    response,
    "Unable to resume translation job."
  );
}
