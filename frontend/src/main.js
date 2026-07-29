import { uploadSrt } from "./api.js";

const API_BASE_URL =
  "https://ultimate-ai-translator-v2.onrender.com";

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

      <div
        id="statusBox"
        style="
          display:none;
          margin-top:25px;
          padding:20px;
          background:#0f172a;
          border-radius:12px;
        "
      >

        <h3 id="statusTitle">
          Translation Status
        </h3>

        <p id="statusText">
          Starting...
        </p>

        <div
          style="
            width:100%;
            height:12px;
            background:#334155;
            border-radius:10px;
            overflow:hidden;
            margin-top:15px;
          "
        >

          <div
            id="progressBar"
            style="
              width:0%;
              height:100%;
              background:#38bdf8;
              transition:width 0.5s ease;
            "
          ></div>

        </div>

        <p id="progressText">
          0%
        </p>

      </div>

      <a
        id="downloadBtn"
        style="
          display:none;
          margin-top:20px;
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

const statusBox =
  document.getElementById("statusBox");

const statusTitle =
  document.getElementById("statusTitle");

const statusText =
  document.getElementById("statusText");

const progressBar =
  document.getElementById("progressBar");

const progressText =
  document.getElementById("progressText");

const downloadBtn =
  document.getElementById("downloadBtn");


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


function updateProgress(
  status,
  progress = null
) {

  statusText.textContent =
    status;


  if (
    typeof progress === "number"
  ) {

    const safeProgress =
      Math.min(
        100,
        Math.max(
          0,
          progress
        )
      );


    progressBar.style.width =
      `${safeProgress}%`;


    progressText.textContent =
      `${safeProgress}%`;

  }

}


async function checkJobStatus(
  jobId
) {

  const response =
    await fetch(
      `${API_BASE_URL}/api/jobs/${jobId}`
    );


  if (!response.ok) {

    throw new Error(
      "Failed to check translation status."
    );

  }


  return await response.json();

}


function getJobProgress(
  job
) {

  if (
    typeof job.progress === "number"
  ) {

    return job.progress;

  }


  if (
    typeof job.progress_percentage === "number"
  ) {

    return job.progress_percentage;

  }


  if (
    typeof job.percentage === "number"
  ) {

    return job.percentage;

  }


  return null;

}


function getJobStatus(
  job
) {

  return (
    job.status ||
    job.state ||
    job.job_status ||
    ""
  )
    .toString()
    .toLowerCase();

}


async function waitForJobCompletion(
  jobId
) {

  while (true) {

    const job =
      await checkJobStatus(
        jobId
      );


    console.log(
      "Job status response:",
      job
    );


    const currentStatus =
      getJobStatus(
        job
      );


    const progress =
      getJobProgress(
        job
      );


    if (
      currentStatus === "completed" ||
      currentStatus === "complete" ||
      currentStatus === "success" ||
      currentStatus === "done"
    ) {

      updateProgress(
        "Translation completed successfully!",
        100
      );

      return job;

    }


    if (
      currentStatus === "failed" ||
      currentStatus === "error"
    ) {

      throw new Error(
        job.error ||
        job.message ||
        "Translation job failed."
      );

    }


    if (
      progress !== null
    ) {

      updateProgress(
        `Translation in progress... ${progress}%`,
        progress
      );

    } else {

      updateProgress(
        "Translation in progress..."
      );

    }


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

      translateBtn.disabled =
        true;


      downloadBtn.style.display =
        "none";


      statusBox.style.display =
        "block";


      statusTitle.textContent =
        "Uploading";


      updateProgress(
        "Uploading SRT file...",
        0
      );


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


      statusTitle.textContent =
        "Translation Started";


      updateProgress(
        `Job created successfully. Job ID: ${jobId}`,
        5
      );


      await waitForJobCompletion(
        jobId
      );


      downloadBtn.href =
        `${API_BASE_URL}/api/jobs/${jobId}/download`;


      downloadBtn.download =
        "translated.srt";


      downloadBtn.style.display =
        "inline-block";


      statusTitle.textContent =
        "Translation Complete";


      alert(
        "Translation completed successfully!"
      );


    } catch (error) {

      console.error(
        "Translation error:",
        error
      );


      statusTitle.textContent =
        "Translation Failed";


      statusText.textContent =
        error.message;


      progressBar.style.width =
        "0%";


      progressText.textContent =
        "";


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
