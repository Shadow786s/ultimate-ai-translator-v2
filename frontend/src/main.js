import {
  uploadSrt,
  getJobStatus,
  getDownloadUrl,
  cancelJob,
  pauseJob,
  resumeJob
} from "./api.js";

document.getElementById("root").innerHTML = `
  <div style="
    min-height:100vh;
    box-sizing:border-box;
    background:
      radial-gradient(circle at top, #1e3a5f 0%, #0f172a 45%, #020617 100%);
    color:#f8fafc;
    padding:30px 16px;
    font-family:Arial, sans-serif;
  ">

    <div style="
      max-width:720px;
      margin:0 auto;
      text-align:center;
    ">

      <h1 style="
        margin:20px 0 8px;
        font-size:36px;
      ">
        Ultimate AI Translator
      </h1>

      <p style="
        margin:0 0 35px;
        color:#94a3b8;
        font-size:16px;
      ">
        Translate your SRT subtitles into natural Indian Hinglish
      </p>

      <div style="
        background:rgba(30,41,59,0.9);
        border:1px solid #334155;
        border-radius:20px;
        padding:30px;
        box-shadow:0 20px 50px rgba(0,0,0,0.35);
        text-align:left;
      ">

        <h2 style="
          margin-top:0;
          text-align:center;
        ">
          Subtitle Translation
        </h2>

        <label style="
          display:block;
          margin-bottom:10px;
          font-weight:bold;
        ">
          Select SRT File
        </label>

        <input
          id="fileInput"
          type="file"
          accept=".srt"
          style="
            width:100%;
            box-sizing:border-box;
            padding:12px;
            background:#0f172a;
            color:#e2e8f0;
            border:1px solid #475569;
            border-radius:10px;
            cursor:pointer;
          "
        />

        <p
          id="fileName"
          style="
            margin:12px 0;
            color:#94a3b8;
            word-break:break-word;
          "
        >
          No file selected
        </p>

        <p
          id="fileSize"
          style="
            margin:8px 0;
            color:#94a3b8;
          "
        >
          File size: -
        </p>

        <p
          id="subtitleCount"
          style="
            margin:8px 0 25px;
            color:#94a3b8;
          "
        >
          Subtitle lines: -
        </p>

        <label style="
          display:block;
          margin-bottom:10px;
          font-weight:bold;
        ">
          Target Language
        </label>

        <div style="
          background:#0f172a;
          border:1px solid #475569;
          border-radius:10px;
          padding:12px;
          margin-bottom:25px;
          color:#38bdf8;
          font-weight:bold;
        ">
          Indian Hinglish
        </div>

        <label
          for="batchSize"
          style="
            display:block;
            margin-bottom:10px;
            font-weight:bold;
          "
        >
          Batch Size
        </label>

        <p style="
          margin:0 0 10px;
          color:#94a3b8;
          font-size:14px;
        ">
          Choose a value between 1 and 500.
        </p>

        <input
          id="batchSize"
          type="number"
          min="1"
          max="500"
          value="100"
          style="
            width:140px;
            box-sizing:border-box;
            padding:12px;
            background:#0f172a;
            color:#f8fafc;
            border:1px solid #475569;
            border-radius:10px;
            font-size:16px;
          "
        />

        <button
          id="translateBtn"
          style="
            width:100%;
            margin-top:30px;
            padding:15px;
            border:none;
            border-radius:12px;
            background:#2563eb;
            color:white;
            font-size:17px;
            font-weight:bold;
            cursor:pointer;
          "
        >
          Start Translation
        </button>

        <div
          id="statusBox"
          style="
            margin-top:30px;
            display:none;
            background:#0f172a;
            border:1px solid #334155;
            border-radius:14px;
            padding:20px;
          "
        >

          <p
            id="jobStatus"
            style="
              margin:0 0 12px;
              font-weight:bold;
            "
          >
            Starting...
          </p>

          <p
            id="progressText"
            style="
              margin:0 0 12px;
              color:#94a3b8;
            "
          >
            Progress: 0%
          </p>

          <p
            id="currentBatchText"
            style="
              margin:0 0 12px;
              color:#94a3b8;
            "
          >
            Current Batch: 0 / 0
          </p>

          <p
            id="etaText"
            style="
              margin:0 0 12px;
              color:#38bdf8;
            "
          >
            ETA: Calculating...
          </p>

          <p
            id="speedText"
            style="
              margin:0 0 12px;
              color:#22c55e;
            "
          >
            Speed: Calculating...
          </p>

          <div
            id="translationPreviewBox"
            style="
              margin-top:25px;
              padding:20px;
              background:#020617;
              border-radius:12px;
              text-align:left;
              display:none;
              max-height:400px;
              overflow-y:auto;
            "
          >

            <h3 style="
              margin-top:0;
              color:#38bdf8;
            ">
              Live Hinglish Translation
            </h3>

            <pre
              id="translationPreview"
              style="
                white-space:pre-wrap;
                word-break:break-word;
                color:#e2e8f0;
                font-family:Arial;
                line-height:1.6;
              "
            ></pre>

          </div>

          <div
            style="
              width:100%;
              height:24px;
              background:#1e293b;
              border-radius:20px;
              overflow:hidden;
              position:relative;
            "
          >

            <div
              id="progressBar"
              style="
                width:0%;
                height:100%;
                background:#22c55e;
                border-radius:20px;
                transition:width 0.5s ease;
                position:relative;
                display:flex;
                align-items:center;
                justify-content:center;
              "
            >

              <span
                id="progressPercent"
                style="
                  position:absolute;
                  left:50%;
                  top:50%;
                  transform:translate(-50%, -50%);
                  color:white;
                  font-size:13px;
                  font-weight:bold;
                  white-space:nowrap;
                "
              >
                0%
              </span>

            </div>

          </div>

          <button
            id="pauseBtn"
            style="
              width:100%;
              margin-top:10px;
              padding:14px;
              border:none;
              border-radius:10px;
              background:#f59e0b;
              color:white;
              font-size:16px;
              font-weight:bold;
              cursor:pointer;
              display:none;
            "
          >
            Pause Translation
          </button>

          <button
            id="cancelBtn"
            style="
              width:100%;
              margin-top:10px;
              padding:14px;
              border:none;
              border-radius:10px;
              background:#dc2626;
              color:white;
              font-size:16px;
              font-weight:bold;
              cursor:pointer;
              display:none;
            "
          >
            Cancel Translation
          </button>

          <div id="downloadContainer"></div>

        </div>

      </div>

    </div>

  </div>
`;


/* =========================================================
   DOM ELEMENTS
========================================================= */

const fileInput =
  document.getElementById("fileInput");

const fileName =
  document.getElementById("fileName");

const fileSize =
  document.getElementById("fileSize");

const subtitleCount =
  document.getElementById("subtitleCount");

const batchSizeInput =
  document.getElementById("batchSize");

const translateBtn =
  document.getElementById("translateBtn");

const statusBox =
  document.getElementById("statusBox");

const jobStatus =
  document.getElementById("jobStatus");

const progressText =
  document.getElementById("progressText");

const currentBatchText =
  document.getElementById("currentBatchText");

const etaText =
  document.getElementById("etaText");

const speedText =
  document.getElementById("speedText");

const progressBar =
  document.getElementById("progressBar");

const progressPercent =
  document.getElementById("progressPercent");

const pauseBtn =
  document.getElementById("pauseBtn");

const cancelBtn =
  document.getElementById("cancelBtn");

const translationPreviewBox =
  document.getElementById(
    "translationPreviewBox"
  );

const translationPreview =
  document.getElementById(
    "translationPreview"
  );

const downloadContainer =
  document.getElementById(
    "downloadContainer"
  );


/* =========================================================
   LOCAL STORAGE KEYS
========================================================= */

const STORAGE_KEYS = {
  JOB_ID:
    "ultimate_ai_translator_active_job_id",

  BATCH_SIZE:
    "ultimate_ai_translator_batch_size",

  FILE_NAME:
    "ultimate_ai_translator_file_name",

  FILE_SIZE:
    "ultimate_ai_translator_file_size",

  SUBTITLE_COUNT:
    "ultimate_ai_translator_subtitle_count",

  START_TIME:
    "ultimate_ai_translator_start_time",
};


/* =========================================================
   RUNTIME STATE
========================================================= */

let activeJobId =
  localStorage.getItem(
    STORAGE_KEYS.JOB_ID
  );

let isPaused = false;

let pollTimer = null;

let retryCountdownTimer = null;

let retryCountdownValue = 0;

let retryCountdownJobId = null;

let translationStartTime =
  Number(
    localStorage.getItem(
      STORAGE_KEYS.START_TIME
    ) || 0
  );


/* =========================================================
   RESTORE SAVED UI DATA
========================================================= */

function restoreSavedUI() {

  const savedBatchSize =
    localStorage.getItem(
      STORAGE_KEYS.BATCH_SIZE
    );

  if (savedBatchSize) {

    batchSizeInput.value =
      savedBatchSize;

  }


  const savedFileName =
    localStorage.getItem(
      STORAGE_KEYS.FILE_NAME
    );

  if (savedFileName) {

    fileName.textContent =
      "File: " +
      savedFileName;

  }


  const savedFileSize =
    localStorage.getItem(
      STORAGE_KEYS.FILE_SIZE
    );

  if (savedFileSize) {

    fileSize.textContent =
      "File size: " +
      savedFileSize;

  }


  const savedSubtitleCount =
    localStorage.getItem(
      STORAGE_KEYS.SUBTITLE_COUNT
    );

  if (savedSubtitleCount) {

    subtitleCount.textContent =
      "Subtitle lines: " +
      savedSubtitleCount;

  }

}


/* =========================================================
   CLEAR ACTIVE JOB STORAGE
========================================================= */

function clearActiveJobStorage() {

  localStorage.removeItem(
    STORAGE_KEYS.JOB_ID
  );

  localStorage.removeItem(
    STORAGE_KEYS.FILE_NAME
  );

  localStorage.removeItem(
    STORAGE_KEYS.FILE_SIZE
  );

  localStorage.removeItem(
    STORAGE_KEYS.SUBTITLE_COUNT
  );

  localStorage.removeItem(
    STORAGE_KEYS.START_TIME
  );

  activeJobId =
    null;

  translationStartTime =
    0;

}


/* =========================================================
   RESET RETRY STATE
========================================================= */

function clearRetryState() {

  if (retryCountdownTimer) {

    clearInterval(
      retryCountdownTimer
    );

    retryCountdownTimer =
      null;

  }

  retryCountdownValue =
    0;

  retryCountdownJobId =
    null;

}


/* =========================================================
   FORMAT FILE SIZE
========================================================= */

function formatFileSize(
  bytes
) {

  const sizeInKB =
    bytes / 1024;

  if (
    sizeInKB < 1024
  ) {

    return (
      sizeInKB.toFixed(2) +
      " KB"
    );

  }

  const sizeInMB =
    sizeInKB / 1024;

  return (
    sizeInMB.toFixed(2) +
    " MB"
  );

}


/* =========================================================
   FILE SELECTION
========================================================= */

fileInput.addEventListener(
  "change",
  async () => {

    if (
      fileInput.files.length === 0
    ) {

      fileName.textContent =
        "No file selected";

      fileSize.textContent =
        "File size: -";

      subtitleCount.textContent =
        "Subtitle lines: -";

      return;

    }


    const file =
      fileInput.files[0];


    fileName.textContent =
      "File: " +
      file.name;


    const formattedSize =
      formatFileSize(
        file.size
      );


    fileSize.textContent =
      "File size: " +
      formattedSize;


    localStorage.setItem(
      STORAGE_KEYS.FILE_NAME,
      file.name
    );


    localStorage.setItem(
      STORAGE_KEYS.FILE_SIZE,
      formattedSize
    );


    try {

      const content =
        await file.text();


      const subtitleBlocks =
        content
          .trim()
          .split(
            /\r?\n\r?\n/
          )
          .filter(
            block =>
              block.trim().length > 0
          );


      subtitleCount.textContent =
        "Subtitle lines: " +
        subtitleBlocks.length;


      localStorage.setItem(
        STORAGE_KEYS.SUBTITLE_COUNT,
        String(
          subtitleBlocks.length
        )
      );


    } catch (error) {

      subtitleCount.textContent =
        "Subtitle lines: Unable to detect";

    }

  }
);


/* =========================================================
   SAVE BATCH SIZE
========================================================= */

batchSizeInput.addEventListener(
  "change",
  () => {

    localStorage.setItem(
      STORAGE_KEYS.BATCH_SIZE,
      batchSizeInput.value
    );

  }
);


/* =========================================================
   DISABLE / ENABLE START BUTTON
========================================================= */

function setTranslationButtonBusy(
  busy
) {

  translateBtn.disabled =
    busy;

  translateBtn.style.opacity =
    busy
      ? "0.6"
      : "1";

  translateBtn.style.cursor =
    busy
      ? "not-allowed"
      : "pointer";

  translateBtn.textContent =
    busy
      ? "Translation Running..."
      : "Start Translation";

}


/* =========================================================
   SHOW DOWNLOAD BUTTON
========================================================= */

function showDownloadButton(
  jobId,
  originalFilename
) {

  downloadContainer.innerHTML =
    "";


  const downloadButton =
    document.createElement(
      "button"
    );


  downloadButton.textContent =
    "Download Translated SRT";


  downloadButton.style.width =
    "100%";

  downloadButton.style.marginTop =
    "20px";

  downloadButton.style.padding =
    "14px";

  downloadButton.style.border =
    "none";

  downloadButton.style.borderRadius =
    "10px";

  downloadButton.style.background =
    "#16a34a";

  downloadButton.style.color =
    "white";

  downloadButton.style.fontSize =
    "16px";

  downloadButton.style.fontWeight =
    "bold";

  downloadButton.style.cursor =
    "pointer";


  downloadButton.onclick =
    () => {

      window.location.href =
        getDownloadUrl(
          jobId
        );

    };


  downloadContainer.appendChild(
    downloadButton
  );

}


/* =========================================================
   SHOW / HIDE CONTROL BUTTONS
========================================================= */

function hideJobControls() {

  pauseBtn.style.display =
    "none";

  cancelBtn.style.display =
    "none";

}


function showJobControls() {

  pauseBtn.style.display =
    "block";

  cancelBtn.style.display =
    "block";

}


/* =========================================================
   RETRY COUNTDOWN
========================================================= */

function startRetryCountdown(
  jobId,
  retrySeconds,
  retryMessage
) {

  if (
    retryCountdownJobId === jobId &&
    retryCountdownValue > 0
  ) {

    return;

  }


  clearRetryState();


  retryCountdownJobId =
    jobId;

  retryCountdownValue =
    Math.max(
      0,
      Number(
        retrySeconds
      )
    );


  const updateRetryUI =
    () => {

      jobStatus.textContent =
        `⚠️ ${
          retryMessage ||
          "Gemini quota limit reached."
        }`;


      progressText.textContent =
        `🔄 Retrying automatically... ${
          retryCountdownValue
        }s`;


      etaText.textContent =
        "ETA: Waiting for retry...";

    };


  updateRetryUI();


  retryCountdownTimer =
    setInterval(
      () => {

        if (
          retryCountdownValue > 0
        ) {

          retryCountdownValue--;

          updateRetryUI();

        }


        if (
          retryCountdownValue <= 0
        ) {

          clearRetryState();

        }

      },
      1000
    );

}


/* =========================================================
   RESTORE JOB UI FROM BACKEND
========================================================= */

function updateJobUI(
  job,
  batchSize
) {

  const currentProgress =
    Number(
      job.progress || 0
    );


  const completedItems =
    Number(
      job.completed_items || 0
    );


  const totalItems =
    Number(
      job.total_items || 0
    );


  const totalBatches =
    totalItems > 0
      ? Math.ceil(
          totalItems /
          batchSize
        )
      : 0;


  const currentBatch =
    completedItems > 0
      ? Math.ceil(
          completedItems /
          batchSize
        )
      : 0;


  jobStatus.textContent =
    "Status: " +
    job.status;


  currentBatchText.textContent =
    "Current Batch: " +
    currentBatch +
    " / " +
    totalBatches;


  progressBar.style.width =
    currentProgress +
    "%";


  progressPercent.textContent =
    currentProgress +
    "%";


  if (
    job.translation_preview
  ) {

    translationPreviewBox.style.display =
      "block";

    translationPreview.textContent =
      job.translation_preview;

  }


  if (
    job.status ===
    "paused"
  ) {

    isPaused =
      true;

    pauseBtn.textContent =
      "Resume Translation";

    pauseBtn.style.background =
      "#16a34a";

    jobStatus.textContent =
      "Translation Paused";

  } else {

    isPaused =
      false;

    pauseBtn.textContent =
      "Pause Translation";

    pauseBtn.style.background =
      "#f59e0b";

  }


  if (
    job.status ===
    "retrying"
  ) {

    startRetryCountdown(
      job.id,
      Number(
        job.retry_seconds || 0
      ),
      job.retry_message
    );

  } else {

    clearRetryState();

    progressText.textContent =
      "Progress: " +
      currentProgress +
      "%";

  }


  if (
    job.status ===
    "completed"
  ) {

    progressBar.style.width =
      "100%";

    progressPercent.textContent =
      "100%";

    progressText.textContent =
      "Progress: 100%";

    jobStatus.textContent =
      "Translation completed successfully!";

    etaText.textContent =
      "ETA: Completed";

    speedText.textContent =
      "Speed: Completed";


    showDownloadButton(
      job.id,
      job.original_filename
    );


    hideJobControls();


    setTranslationButtonBusy(
      false
    );


    clearActiveJobStorage();


    return "completed";

  }


  if (
    job.status ===
    "failed"
  ) {

    jobStatus.textContent =
      "Translation failed";

    progressText.textContent =
      job.error_message ||
      "Translation failed.";

    etaText.textContent =
      "ETA: Failed";

    speedText.textContent =
      "Speed: Failed";


    hideJobControls();


    setTranslationButtonBusy(
      false
    );


    clearActiveJobStorage();


    return "failed";

  }


  if (
    job.status ===
    "cancelled"
  ) {

    jobStatus.textContent =
      "Translation Cancelled";

    progressText.textContent =
      "Translation Cancelled — Progress: " +
      currentProgress +
      "%";

    etaText.textContent =
      "ETA: Cancelled";

    speedText.textContent =
      "Speed: Cancelled";


    hideJobControls();


    setTranslationButtonBusy(
      false
    );


    clearActiveJobStorage();


    return "cancelled";

  }


  showJobControls();


  return "active";

}


/* =========================================================
   POLLING
========================================================= */

async function pollJob(
  jobId,
  batchSize
) {

  if (
    pollTimer
  ) {

    clearTimeout(
      pollTimer
    );

    pollTimer =
      null;

  }


  try {

    const status =
      await getJobStatus(
        jobId
      );


    const job =
      status.job;


    const result =
      updateJobUI(
        job,
        batchSize
      );


    if (
      result ===
      "completed" ||
      result ===
      "failed" ||
      result ===
      "cancelled"
    ) {

      return;

    }


    const completedItems =
      Number(
        job.completed_items || 0
      );


    const currentProgress =
      Number(
        job.progress || 0
      );


    if (
      translationStartTime <= 0
    ) {

      translationStartTime =
        Date.now();

      localStorage.setItem(
        STORAGE_KEYS.START_TIME,
        String(
          translationStartTime
        )
      );

    }


    const elapsedSeconds =
      (
        Date.now() -
        translationStartTime
      ) / 1000;


    if (
      completedItems > 0 &&
      elapsedSeconds > 0
    ) {

      const speed =
        completedItems /
        elapsedSeconds;


      speedText.textContent =
        "Speed: " +
        speed.toFixed(2) +
        " subtitles/sec";

    } else {

      speedText.textContent =
        "Speed: Calculating...";

    }


    if (
      job.status !==
      "retrying" &&
      currentProgress > 0
    ) {

      const estimatedTotalSeconds =
        elapsedSeconds /
        (
          currentProgress /
          100
        );


      const remainingSeconds =
        Math.max(
          0,
          estimatedTotalSeconds -
          elapsedSeconds
        );


      const minutes =
        Math.floor(
          remainingSeconds /
          60
        );


      const seconds =
        Math.floor(
          remainingSeconds %
          60
        );


      etaText.textContent =
        `ETA: ${
          minutes
        }m ${
          seconds
        }s`;

    } else if (
      job.status !==
      "retrying"
    ) {

      etaText.textContent =
        "ETA: Calculating...";

    }


    pollTimer =
      setTimeout(
        () => {

          pollJob(
            jobId,
            batchSize
          );

        },
        2000
      );


  } catch (error) {

    console.error(
      "Job polling error:",
      error
    );


    jobStatus.textContent =
      "Connection temporarily unavailable";


    progressText.textContent =
      "Trying to reconnect...";


    pollTimer =
      setTimeout(
        () => {

          pollJob(
            jobId,
            batchSize
          );

        },
        5000
      );

  }

}


/* =========================================================
   PAUSE / RESUME
========================================================= */

async function handlePauseResume() {

  if (
    !activeJobId
  ) {

    return;

  }


  try {

    pauseBtn.disabled =
      true;


    if (
      !isPaused
    ) {

      pauseBtn.textContent =
        "Pausing...";


      await pauseJob(
        activeJobId
      );


      isPaused =
        true;


      pauseBtn.textContent =
        "Resume Translation";


      pauseBtn.style.background =
        "#16a34a";


      jobStatus.textContent =
        "Translation Paused";


    } else {

      pauseBtn.textContent =
        "Resuming...";


      await resumeJob(
        activeJobId
      );


      isPaused =
        false;


      pauseBtn.textContent =
        "Pause Translation";


      pauseBtn.style.background =
        "#f59e0b";


      jobStatus.textContent =
        "Translation Resumed";

    }


    await pollJob(
      activeJobId,
      Number(
        batchSizeInput.value
      )
    );


  } catch (error) {

    console.error(
      "Pause/resume error:",
      error
    );


    alert(
      error.message
    );


  } finally {

    pauseBtn.disabled =
      false;

  }

}


/* =========================================================
   CANCEL
========================================================= */

async function handleCancel() {

  if (
    !activeJobId
  ) {

    return;

  }


  try {

    cancelBtn.disabled =
      true;


    cancelBtn.textContent =
      "Cancelling...";


    await cancelJob(
      activeJobId
    );


    jobStatus.textContent =
      "Translation cancellation requested";


    cancelBtn.textContent =
      "Cancellation Requested";


    await pollJob(
      activeJobId,
      Number(
        batchSizeInput.value
      )
    );


  } catch (error) {

    console.error(
      "Cancel error:",
      error
    );


    cancelBtn.disabled =
      false;


    cancelBtn.textContent =
      "Cancel Translation";


    alert(
      error.message
    );

  }

}


/* =========================================================
   BUTTON EVENTS
========================================================= */

pauseBtn.addEventListener(
  "click",
  handlePauseResume
);


cancelBtn.addEventListener(
  "click",
  handleCancel
);


/* =========================================================
   START NEW TRANSLATION
========================================================= */

translateBtn.addEventListener(
  "click",
  async () => {

    if (
      fileInput.files.length === 0
    ) {

      alert(
        "Please select an SRT file first."
      );

      return;

    }


    const batchSize =
      Number(
        batchSizeInput.value
      );


    if (
      !Number.isInteger(
        batchSize
      ) ||
      batchSize < 1 ||
      batchSize > 500
    ) {

      alert(
        "Batch size must be a whole number between 1 and 500."
      );

      return;

    }


    localStorage.setItem(
      STORAGE_KEYS.BATCH_SIZE,
      String(
        batchSize
      )
    );


    const file =
      fileInput.files[0];


    localStorage.setItem(
      STORAGE_KEYS.FILE_NAME,
      file.name
    );


    localStorage.setItem(
      STORAGE_KEYS.FILE_SIZE,
      formatFileSize(
        file.size
      )
    );


    try {

      setTranslationButtonBusy(
        true
      );


      statusBox.style.display =
        "block";


      hideJobControls();


      downloadContainer.innerHTML =
        "";


      translationPreviewBox.style.display =
        "none";


      translationPreview.textContent =
        "";


      progressBar.style.width =
        "0%";


      progressPercent.textContent =
        "0%";


      progressText.textContent =
        "Progress: 0%";


      currentBatchText.textContent =
        "Current Batch: 0 / 0";


      etaText.textContent =
        "ETA: Calculating...";


      speedText.textContent =
        "Speed: Calculating...";


      jobStatus.textContent =
        "Uploading SRT file...";


      clearRetryState();


      const result =
        await uploadSrt(
          file,
          batchSize
        );


      activeJobId =
        result.job_id;


      localStorage.setItem(
        STORAGE_KEYS.JOB_ID,
        activeJobId
      );


      translationStartTime =
        Date.now();


      localStorage.setItem(
        STORAGE_KEYS.START_TIME,
        String(
          translationStartTime
        )
      );


      jobStatus.textContent =
        "Translation started";


      await pollJob(
        activeJobId,
        batchSize
      );


    } catch (error) {

      console.error(
        "Translation start error:",
        error
      );


      jobStatus.textContent =
        "Translation failed";


      progressText.textContent =
        error.message;


      etaText.textContent =
        "ETA: Failed";


      speedText.textContent =
        "Speed: Failed";


      alert(
        error.message
      );


      clearActiveJobStorage();

    } finally {

      if (
        !activeJobId
      ) {

        setTranslationButtonBusy(
          false
        );

      }

    }

  }
);


/* =========================================================
   PAGE LOAD / REFRESH RESTORE
========================================================= */

async function restoreActiveJob() {

  restoreSavedUI();


  if (
    !activeJobId
  ) {

    return;

  }


  const savedBatchSize =
    Number(
      localStorage.getItem(
        STORAGE_KEYS.BATCH_SIZE
      ) ||
      batchSizeInput.value ||
      100
    );


  batchSizeInput.value =
    savedBatchSize;


  statusBox.style.display =
    "block";


  setTranslationButtonBusy(
    true
  );


  jobStatus.textContent =
    "Restoring translation job...";


  progressText.textContent =
    "Loading latest progress...";


  try {

    const status =
      await getJobStatus(
        activeJobId
      );


    const job =
      status.job;


    /*
      IMPORTANT:

      Agar browser refresh ke baad bhi job backend par
      processing/paused/retrying state mein hai,
      hum same job ko monitor karenge.
    */


    const result =
      updateJobUI(
        job,
        savedBatchSize
      );


    if (
      result ===
      "completed" ||
      result ===
      "failed" ||
      result ===
      "cancelled"
    ) {

      return;

    }


    /*
      Refresh ke baad ETA ke liye exact original
      frontend start time available ho sakta hai.
    */

    if (
      translationStartTime <= 0
    ) {

      translationStartTime =
        Date.now();

      localStorage.setItem(
        STORAGE_KEYS.START_TIME,
        String(
          translationStartTime
        )
      );

    }


    jobStatus.textContent =
      "Translation restored";


    await pollJob(
      activeJobId,
      savedBatchSize
    );


  } catch (error) {

    console.error(
      "Unable to restore active job:",
      error
    );


    /*
      Job not found hone par stale localStorage
      clear kar do.

      Lekin temporary network error mein
      localStorage clear nahi karna chahiye.
    */

    if (
      error.message &&
      error.message.toLowerCase()
        .includes(
          "job not found"
        )
    ) {

      clearActiveJobStorage();

      setTranslationButtonBusy(
        false
      );

      hideJobControls();

      statusBox.style.display =
        "none";

    } else {

      jobStatus.textContent =
        "Unable to reconnect to translation job";

      progressText.textContent =
        "The job may still be running. Retrying...";


      setTranslationButtonBusy(
        true
      );


      setTimeout(
        () => {

          restoreActiveJob();

        },
        5000
      );

    }

  }

}


/* =========================================================
   INITIALIZE APP
========================================================= */

restoreActiveJob();
