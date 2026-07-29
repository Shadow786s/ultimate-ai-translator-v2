import { uploadSrt } from "./api.js";

document.getElementById("root").innerHTML = `
  <div style="
    min-height:100vh;
    background:#0f172a;
    color:white;
    padding:50px 20px;
    font-family:Arial,sans-serif;
    text-align:center;
  ">

    <h1>Ultimate AI Translator</h1>

    <p>
      Translate your SRT subtitles into natural Hinglish using AI.
    </p>

    <div style="
      margin:40px auto;
      max-width:500px;
      padding:30px;
      background:#1e293b;
      border-radius:20px;
    ">

      <h2>Upload SRT File</h2>

      <input
        id="fileInput"
        type="file"
        accept=".srt"
      />

      <p id="fileName">
        No file selected
      </p>

      <button
        id="translateBtn"
        style="
          padding:12px 25px;
          border:none;
          border-radius:8px;
          cursor:pointer;
        "
      >
        Start Translation
      </button>

      <p id="status"></p>

      <a
        id="downloadBtn"
        style="
          display:none;
          color:#38bdf8;
          font-weight:bold;
          text-decoration:none;
        "
      >
        Download Translated SRT
      </a>

    </div>
  </div>
`;

const fileInput =
  document.getElementById("fileInput");

const fileName =
  document.getElementById("fileName");

const translateBtn =
  document.getElementById("translateBtn");

const status =
  document.getElementById("status");

const downloadBtn =
  document.getElementById("downloadBtn");

const API_BASE_URL =
  "https://ultimate-ai-translator-v2.onrender.com";


fileInput.addEventListener(
  "change",
  () => {

    if (
      fileInput.files.length === 0
    ) {
      fileName.textContent =
        "No file selected";

      return;
    }

    fileName.textContent =
      fileInput.files[0].name;

  }
);


async function checkJobStatus(jobId) {

  const response =
    await fetch(
      `${API_BASE_URL}/api/jobs/${jobId}`
    );

  if (!response.ok) {

    throw new Error(
      "Failed to check job status."
    );

  }

  return await response.json();

}


async function waitForJobCompletion(jobId) {

  while (true) {

    const job =
      await checkJobStatus(jobId);

    console.log(
      "Job status:",
      job
    );

    const currentStatus =
      job.status ||
      job.state;

    if (
      currentStatus === "completed" ||
      currentStatus === "complete" ||
      currentStatus === "success"
    ) {

      return job;

    }

    if (
      currentStatus === "failed" ||
      currentStatus === "error"
    ) {

      throw new Error(
        job.error ||
        "Translation job failed."
      );

    }

    status.textContent =
      "Translation in progress...";

    await new Promise(
      resolve =>
        setTimeout(
          resolve,
          3000
        )
    );

  }

}


translateBtn.addEventListener(
  "click",
  async () => {

    if (
      fileInput.files.length === 0
    ) {

      alert(
        "Please select an SRT file."
      );

      return;

    }


    try {

      translateBtn.disabled = true;

      downloadBtn.style.display =
        "none";

      status.textContent =
        "Uploading SRT file...";


      const result =
        await uploadSrt(
          fileInput.files[0],
          100
        );


      const jobId =
        result.job_id;


      if (!jobId) {

        throw new Error(
          "Backend did not return a Job ID."
        );

      }


      status.textContent =
        "Job created. Translation started...";


      await waitForJobCompletion(
        jobId
      );


      status.textContent =
        "Translation completed successfully!";


      downloadBtn.href =
        `${API_BASE_URL}/api/jobs/${jobId}/download`;

      downloadBtn.download =
        "translated.srt";

      downloadBtn.style.display =
        "inline-block";


      alert(
        "Translation completed successfully!"
      );


    } catch (error) {

      console.error(
        error
      );

      status.textContent =
        "Translation failed.";

      alert(
        error.message
      );


    } finally {

      translateBtn.disabled =
        false;

      translateBtn.textContent =
        "Start Translation";

    }

  }
);
