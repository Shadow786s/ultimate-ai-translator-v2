import {
  uploadSrt,
  getJobStatus,
  getDownloadUrl,
  cancelJob,
  pauseJob,
  resumeJob,
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
            margin:12px 0 8px;
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


          <div style="
            width:100%;
            height:24px;
            background:#1e293b;
            border-radius:20px;
            overflow:hidden;
            position:relative;
          ">

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
                min-width:0;
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


          <div
            id="downloadContainer"
            style="
              margin-top:20px;
            "
          ></div>


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

const translateBtn =
  document.getElementById("translateBtn");

const statusBox =
  document.getElementById("statusBox");

const jobStatus =
  document.getElementById("jobStatus");

const progressText =
  document.getElementById("progressText");

const currentBatchText =
  document.getElementById(
    "currentBatchText"
  );

const etaText =
  document.getElementById("etaText");

const speedText =
  document.getElementById("speedText");

const progressBar =
  document.getElementById("progressBar");

const progressPercent =
  document.getElementById(
    "progressPercent"
  );

const batchSizeInput =
  document.getElementById("batchSize");

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
   STATE
========================================================= */

let currentJobId = null;

let isPaused = false;

let isCancelling = false;

let retryCountdownTimer = null;

let retryCountdownValue = 0;

let retryCountdownJobId = null;


/* =========================================================
   HELPER FUNCTIONS
========================================================= */

function clearRetryCountdown() {

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


function resetDownloadButton() {

  downloadContainer.innerHTML =
    "";

}


function showDownloadButton(
  jobId
) {

  resetDownloadButton();

  const downloadButton =
    document.createElement(
      "button"
    );

  downloadButton.textContent =
    "Download Translated SRT";

  downloadButton.style.width =
    "100%";

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

      const downloadUrl =
        getDownloadUrl(
          jobId
        );

      window.location.href =
        downloadUrl;

    };

  downloadContainer.appendChild(
    downloadButton
  );

}


function resetProgressUI() {

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

  translationPreviewBox.style.display =
    "none";

  translationPreview.textContent =
    "";

}


function setPauseButtonPausedState() {

  pauseBtn.textContent =
    "Resume Translation";

  pauseBtn.style.background =
    "#16a34a";

}


function setPauseButtonRunningState() {

  pauseBtn.textContent =
    "Pause Translation";

  pauseBtn.style.background =
    "#f59e0b";

}


function setPauseButtonDisabledState(
  text
) {

  pauseBtn.disabled =
    true;

  pauseBtn.textContent =
    text;

}


function setCancelButtonCancelledState() {

  cancelBtn.textContent =
    "Translation Cancelled";

  cancelBtn.disabled =
    true;

  cancelBtn.style.background =
    "#64748b";

}


function calculateETA(
  progress,
  startTime
) {

  if (
    progress <= 0
  ) {

    return "ETA: Calculating...";

  }

  const elapsedSeconds =
    (
      Date.now() -
      startTime
    ) / 1000;

  if (
    elapsedSeconds <= 0
  ) {

    return "ETA: Calculating...";

  }

  const estimatedTotalSeconds =
    elapsedSeconds /
    (
      progress /
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

  return (
    `ETA: ${minutes}m ${seconds}s`
  );

}


/* =========================================================
   FILE SELECT
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


    const sizeInKB =
      file.size /
      1024;


    if (
      sizeInKB < 1024
    ) {

      fileSize.textContent =
        "File size: " +
        sizeInKB.toFixed(2) +
        " KB";

    } else {

      const sizeInMB =
        sizeInKB /
        1024;

      fileSize.textContent =
        "File size: " +
        sizeInMB.toFixed(2) +
        " MB";

    }


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

    } catch (error) {

      subtitleCount.textContent =
        "Subtitle lines: Unable to detect";

    }

  }
);


/* =========================================================
   PAUSE / RESUME
========================================================= */

pauseBtn.addEventListener(
  "click",
  async () => {

    if (
      !currentJobId
    ) {

      return;

    }


    if (
      isCancelling
    ) {

      return;

    }


    try {

      pauseBtn.disabled =
        true;


      if (
        !isPaused
      ) {

        /* =========================
           PAUSE
        ========================= */

        pauseBtn.textContent =
          "Pausing...";


        const result =
          await pauseJob(
            currentJobId
          );


        if (
          result.status ===
          "paused"
        ) {

          isPaused =
            true;

          setPauseButtonPausedState();

          jobStatus.textContent =
            "Translation Paused";

          etaText.textContent =
            "ETA: Paused";

        } else {

          throw new Error(
            result.message ||
            "Unable to pause translation."
          );

        }

      } else {

        /* =========================
           RESUME
        ========================= */

        pauseBtn.textContent =
          "Resuming...";


        const result =
          await resumeJob(
            currentJobId
          );


        if (
          result.status ===
          "processing"
        ) {

          isPaused =
            false;

          setPauseButtonRunningState();

          jobStatus.textContent =
            "Translation Resumed";

          etaText.textContent =
            "ETA: Calculating...";

        } else {

          throw new Error(
            result.message ||
            "Unable to resume translation."
          );

        }

      }

    } catch (error) {

      alert(
        error.message
      );

      if (
        isPaused
      ) {

        setPauseButtonPausedState();

      } else {

        setPauseButtonRunningState();

      }

    } finally {

      pauseBtn.disabled =
        false;

    }

  }
);


/* =========================================================
   START TRANSLATION
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


    /* =========================
       RESET JOB STATE
    ========================= */

    currentJobId =
      null;

    isPaused =
      false;

    isCancelling =
      false;

    clearRetryCountdown();

    resetDownloadButton();

    resetProgressUI();

    setPauseButtonRunningState();


    try {

      /* =========================
         DISABLE START
      ========================= */

      translateBtn.disabled =
        true;

      translateBtn.style.opacity =
        "0.6";

      translateBtn.style.cursor =
        "not-allowed";

      translateBtn.textContent =
        "Uploading...";


      statusBox.style.display =
        "block";


      pauseBtn.style.display =
        "block";

      pauseBtn.disabled =
        true;


      cancelBtn.style.display =
        "block";

      cancelBtn.disabled =
        false;

      cancelBtn.textContent =
        "Cancel Translation";

      cancelBtn.style.background =
        "#dc2626";


      jobStatus.textContent =
        "Creating translation job...";


      progressText.textContent =
        "Progress: 0%";


      /* =========================
         UPLOAD
      ========================= */

      const result =
        await uploadSrt(
          fileInput.files[0],
          batchSize
        );


      currentJobId =
        result.job_id;


      if (
        !currentJobId
      ) {

        throw new Error(
          "Backend did not return a job ID."
        );

      }


      jobStatus.textContent =
        "Translation started";


      pauseBtn.disabled =
        false;


      /* =========================
         CANCEL HANDLER
      ========================= */

      pauseBtn.onclick = async () => {
  if (!jobId) {
    return;
  }

  try {
    pauseBtn.disabled = true;

    if (!isPaused) {
      pauseBtn.textContent = "Pausing...";

      await pauseJob(jobId);

      isPaused = true;

      pauseBtn.textContent = "Resume Translation";
      pauseBtn.style.background = "#16a34a";

      jobStatus.textContent =
        "Translation Paused — current batch will finish, then translation will pause.";

    } else {
      pauseBtn.textContent = "Resuming...";

      await resumeJob(jobId);

      isPaused = false;

      pauseBtn.textContent = "Pause Translation";
      pauseBtn.style.background = "#f59e0b";

      jobStatus.textContent =
        "Translation Resumed";
    }

  } catch (error) {
    console.error("Pause/Resume error:", error);

    alert(
      error.message ||
      "Unable to pause/resume translation."
    );

  } finally {
    pauseBtn.disabled = false;
  }
};
          
      

      /* =========================
         POLLING START
      ========================= */

      const startTime =
        Date.now();


      let completed =
        false;


      while (
        !completed
      ) {

        await new Promise(
          resolve =>
            setTimeout(
              resolve,
              2000
            )
        );


        if (
          !currentJobId
        ) {

          break;

        }


        const status =
          await getJobStatus(
            currentJobId
          );


        const job =
          status.job;

        if (status.job.status === "paused") {
          isPaused = true;

          pauseBtn.style.display = "block";
          pauseBtn.disabled = false;

          pauseBtn.textContent =
            "Resume Translation";

          pauseBtn.style.background =
            "#16a34a";

          jobStatus.textContent =
            "Translation Paused";

          etaText.textContent =
            "ETA: Paused";

          speedText.textContent =
            "Speed: Paused";
        }

        const currentProgress =
          Number(
            job.progress ||
            0
          );

        if (status.job.status === "processing") {
          isPaused = false;

          pauseBtn.style.display = "block";
          pauseBtn.disabled = false;

          pauseBtn.textContent =
            "Pause Translation";

          pauseBtn.style.background =
            "#f59e0b";

          jobStatus.textContent =
            "Translation Processing";
        }


        /* =========================
           BACKEND STATUS
        ========================= */

        if (
          job.status ===
          "paused"
        ) {

          isPaused =
            true;

          setPauseButtonPausedState();

          pauseBtn.disabled =
            false;

          jobStatus.textContent =
            "Translation Paused";

          etaText.textContent =
            "ETA: Paused";

        }


        else if (
          job.status ===
          "processing"
        ) {

          if (
            !isCancelling
          ) {

            isPaused =
              false;

            setPauseButtonRunningState();

            pauseBtn.disabled =
              false;

            jobStatus.textContent =
              "Status: Processing";

          }

        }


        else if (
          job.status ===
          "retrying"
        ) {

          jobStatus.textContent =
            `⚠️ ${
              job.retry_message ||
              "Gemini quota limit reached."
            }`;

        }


        else if (
          job.status ===
          "queued"
        ) {

          jobStatus.textContent =
            "Status: Queued";

        }


        /* =========================
           RETRY COUNTDOWN
        ========================= */

        const retrySeconds =
          Number(
            job.retry_seconds ||
            0
          );


        const retryMessage =
          job.retry_message ||
          "";


        if (
          retrySeconds > 0
        ) {

          if (
            retryCountdownJobId !==
              currentJobId ||
            retryCountdownValue <= 0
          ) {

            retryCountdownJobId =
              currentJobId;

            retryCountdownValue =
              retrySeconds;


            clearRetryCountdown();


            retryCountdownJobId =
              currentJobId;

            retryCountdownValue =
              retrySeconds;


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


            retryCountdownTimer =
              setInterval(
                () => {

                  if (
                    retryCountdownValue >
                    0
                  ) {

                    retryCountdownValue--;

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

                  }


                  if (
                    retryCountdownValue <=
                    0
                  ) {

                    clearRetryCountdown();

                  }

                },
                1000
              );

          }

        }


        /* =========================
           NORMAL PROGRESS
        ========================= */

        if (
          retryCountdownValue <= 0 &&
          retryCountdownTimer === null &&
          job.status !== "paused"
        ) {

          progressText.textContent =
            "Progress: " +
            currentProgress +
            "%";

        }


        /* =========================
           BATCH INFO
        ========================= */

        const completedItems =
          Number(
            job.completed_items ||
            0
          );


        const totalItems =
          Number(
            job.total_items ||
            0
          );


        const totalBatches =
          Math.ceil(
            totalItems /
            batchSize
          );


        const currentBatch =
          completedItems === 0
            ? 0
            : Math.ceil(
                completedItems /
                batchSize
              );


        currentBatchText.textContent =
          "Current Batch: " +
          currentBatch +
          " / " +
          totalBatches;


        /* =========================
           SPEED
        ========================= */

        const elapsedSeconds =
          (
            Date.now() -
            startTime
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

        }


        /* =========================
           ETA
        ========================= */

        if (
          retryCountdownValue <= 0 &&
          retryCountdownTimer === null &&
          job.status !== "paused"
        ) {

          etaText.textContent =
            calculateETA(
              currentProgress,
              startTime
            );

        }


        /* =========================
           LIVE PREVIEW
        ========================= */

        if (
          job.translation_preview
        ) {

          translationPreviewBox.style.display =
            "block";


          translationPreview.textContent =
            job.translation_preview;

        }


        /* =========================
           PROGRESS BAR
        ========================= */

        progressBar.style.width =
          currentProgress +
          "%";


        progressPercent.textContent =
          currentProgress +
          "%";


        /* =========================
           COMPLETED
        ========================= */

        if (
          job.status ===
          "completed"
        ) {

          completed =
            true;


          clearRetryCountdown();


          jobStatus.textContent =
            "Translation completed successfully!";


          speedText.textContent =
            "Speed: Completed";


          etaText.textContent =
            "ETA: Completed";


          progressText.textContent =
            "Progress: 100%";


          progressBar.style.width =
            "100%";


          progressPercent.textContent =
            "100%";


          pauseBtn.style.display =
            "none";


          cancelBtn.style.display =
            "none";


          showDownloadButton(
            currentJobId
          );


          alert(
            "Translation completed successfully!"
          );

        }


        /* =========================
           FAILED
        ========================= */

        if (
          job.status ===
          "failed"
        ) {

          completed =
            true;


          throw new Error(
            job.error_message ||
            "Translation failed."
          );

        }


        /* =========================
           CANCELLED
        ========================= */

        if (
          job.status ===
          "cancelled"
        ) {

          completed =
            true;


          clearRetryCountdown();


          isCancelling =
            false;


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


          setCancelButtonCancelledState();


          pauseBtn.style.display =
            "none";


          break;

        }

      }


    } catch (error) {

      clearRetryCountdown();


      jobStatus.textContent =
        "Translation failed";


      progressText.textContent =
        error.message;


      progressBar.style.width =
        "0%";


      progressPercent.textContent =
        "0%";


      etaText.textContent =
        "ETA: Failed";


      speedText.textContent =
        "Speed: Failed";


      pauseBtn.style.display =
        "none";


      cancelBtn.style.display =
        "none";


      alert(
        error.message
      );


    } finally {

      clearRetryCountdown();


      translateBtn.disabled =
        false;


      translateBtn.style.opacity =
        "1";


      translateBtn.style.cursor =
        "pointer";


      translateBtn.textContent =
        "Start Translation";


      /*
       * Important:
       * Completed / cancelled / failed state ke baad
       * buttons ko unnecessarily visible mat rakho.
       */

      if (
        !isCancelling &&
        jobStatus.textContent !==
          "Translation completed successfully!"
      ) {

        cancelBtn.style.display =
          "none";

      }


      /*
       * Current job ID ko immediately clear
       * nahi kar rahe, kyunki download button
       * completed job ke liye currentJobId use karta hai.
       */

    }

  }
);
