import {
  uploadSrt,
  getJobStatus,
  getDownloadUrl,
  cancelJob
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
            margin:12px 0 25px;
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
  id="attemptText"
  style="
    margin:0 0 12px;
    color:#f59e0b;
    font-weight:bold;
  "
>
  Attempt: 1 / 5
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
    background:#0f172a;
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

        </div>

      </div>

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

const jobStatus =
  document.getElementById("jobStatus");

const progressText =
  document.getElementById("progressText");

const currentBatchText =
  document.getElementById(
    "currentBatchText"
  );

const attemptText =
  document.getElementById(
    "attemptText"
  );

const etaText =
  document.getElementById("etaText");

const speedText =
  document.getElementById("speedText");

const cancelBtn =
  document.getElementById("cancelBtn");

const progressBar =
  document.getElementById("progressBar");

const progressPercent =
  document.getElementById("progressPercent");

const batchSizeInput =
  document.getElementById("batchSize");

const translationPreviewBox =
  document.getElementById(
    "translationPreviewBox"
  );

const translationPreview =
  document.getElementById(
    "translationPreview"
  );

const fileSize =
  document.getElementById("fileSize");

const subtitleCount =
  document.getElementById("subtitleCount");

let retryCountdownTimer = null;
let retryCountdownValue = 0;
let retryCountdownJobId = null;
let currentAttempt = 0;
const maxAttempts = 5;


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
      file.size / 1024;


    if (
      sizeInKB < 1024
    ) {

      fileSize.textContent =
        "File size: " +
        sizeInKB.toFixed(2) +
        " KB";

    } else {

      const sizeInMB =
        sizeInKB / 1024;

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
      !Number.isInteger(batchSize) ||
      batchSize < 1 ||
      batchSize > 500
    ) {

      alert(
        "Batch size must be a whole number between 1 and 500."
      );

      return;

    }


    try {

      translateBtn.disabled = true;

      translateBtn.style.opacity =
        "0.6";

      translateBtn.style.cursor =
        "not-allowed";

      translateBtn.textContent =
        "Uploading...";

      cancelBtn.style.display =
        "block";

      cancelBtn.disabled =
        false;

      cancelBtn.textContent =
        "Cancel Translation";

      cancelBtn.style.background =
        "#dc2626";

      statusBox.style.display =
        "block";


      jobStatus.textContent =
        "Creating translation job...";


      progressText.textContent =
        "Progress: 0%";


      progressBar.style.width =
        "0%";
      

      const result =
        await uploadSrt(
          fileInput.files[0],
          batchSize
        );


      const jobId =
        result.job_id;

      cancelBtn.style.display =
        "block";

      cancelBtn.disabled =
        false;

      cancelBtn.textContent =
        "Cancel Translation";

      cancelBtn.onclick =
        async () => {

          try {

            cancelBtn.disabled =
              true;

            cancelBtn.textContent =
              "Cancelling...";


            const cancelResult =
              await cancelJob(
                jobId
              );


            jobStatus.textContent =
              "Translation cancellation requested";


            cancelBtn.textContent =
              "Cancellation Requested";


          } catch (error) {

            cancelBtn.disabled =
              false;

            cancelBtn.textContent =
              "Cancel Translation";


            alert(
              error.message
            );

          }

        };

      const startTime =
        Date.now();

      currentAttempt = 0;

      attemptText.textContent =
        `Attempt: ${currentAttempt} / ${maxAttempts}`;
      

      jobStatus.textContent =
        "Translation started";


      let completed = false;


      while (!completed) {

        await new Promise(
          (resolve) =>
            setTimeout(
              resolve,
              2000
            )
        );


        const status =
          await getJobStatus(
            jobId
          );


        const currentProgress =
          Number(
            status.job.progress || 0
          );


        jobStatus.textContent =
          "Status: " +
          status.job.status;

        
        const retrySeconds = Number(
  status.job.retry_seconds || 0
);

const retryMessage =
  status.job.retry_message || "";

if (retrySeconds > 0) {

  // Sirf naya retry cycle start hone par countdown initialize karo
  if (
    retryCountdownJobId !== jobId ||
    retryCountdownValue <= 0
  ) {

    currentAttempt++;
    }

    retryCountdownJobId =
      jobId;

    retryCountdownValue =
      retrySeconds;

    attemptText.textContent =
      `Attempt: ${currentAttempt} / ${maxAttempts}`;

    if (retryCountdownTimer) {

      clearInterval(
        retryCountdownTimer
      );

      retryCountdownTimer =
        null;

    }

    // Initial UI state
    jobStatus.textContent =
      `⚠️ ${
        retryMessage ||
        "Gemini quota limit reached."
      }`;

    progressText.textContent =
      `🔄 Retrying automatically... ${retryCountdownValue}s`;

    etaText.textContent =
      "ETA: Waiting for retry...";


    retryCountdownTimer =
      setInterval(
        () => {

          if (
            retryCountdownValue > 0
          ) {

            retryCountdownValue--;

            jobStatus.textContent =
              `⚠️ ${
                retryMessage ||
                "Gemini quota limit reached."
              }`;

            progressText.textContent =
              `🔄 Retrying automatically... ${retryCountdownValue}s`;

            etaText.textContent =
              "ETA: Waiting for retry...";

          }

          if (
            retryCountdownValue <= 0
          ) {

            clearInterval(
              retryCountdownTimer
            );

            retryCountdownTimer =
              null;

          }

        },
        1000
      );

  } else {

    // Existing retry countdown ko preserve karo
    jobStatus.textContent =
      `⚠️ ${
        retryMessage ||
        "Gemini quota limit reached."
      }`;

    progressText.textContent =
      `🔄 Retrying automatically... ${retryCountdownValue}s`;

    etaText.textContent =
      "ETA: Waiting for retry...";

  }

} else {

  // Retry khatam hone par countdown timer stop karo
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

  // Normal status restore
  jobStatus.textContent =
    "Status: " +
    status.job.status;

}

          
        
        // Normal progress sirf retry countdown ke bahar update karo
if (
  retryCountdownValue <= 0 &&
  retryCountdownTimer === null
) {

  progressText.textContent =
    "Progress: " +
    currentProgress +
    "%";

}


const batchCompletedItems =
  Number(
    status.job.completed_items || 0
  );

const batchTotalItems =
  Number(
    status.job.total_items || 0
  );

const batchTotalCount =
  Math.ceil(
    batchTotalItems / batchSize
  );

const batchCurrentNumber =
  batchCompletedItems === 0
    ? 0
    : Math.ceil(
        batchCompletedItems / batchSize
      );

currentBatchText.textContent =
  "Current Batch: " +
  batchCurrentNumber +
  " / " +
  batchTotalCount;

const completedItems =
  Number(
    status.job.completed_items || 0
  );

const elapsedSeconds =
  (Date.now() - startTime) / 1000;

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

    
  // Normal ETA sirf tab dikhao jab retry countdown active nahi hai
if (
  retryCountdownValue <= 0 &&
  retryCountdownTimer === null
) {

  if (currentProgress > 0) {

    const elapsedSeconds =
      (Date.now() - startTime) / 1000;

    const estimatedTotalSeconds =
      elapsedSeconds /
      (currentProgress / 100);

    const remainingSeconds =
      Math.max(
        0,
        estimatedTotalSeconds -
        elapsedSeconds
      );

    const minutes =
      Math.floor(
        remainingSeconds / 60
      );

    const seconds =
      Math.floor(
        remainingSeconds % 60
      );

    etaText.textContent =
      `ETA: ${minutes}m ${seconds}s`;

  } else {

    etaText.textContent =
      "ETA: Calculating...";

  }

}

        if (
          status.job.translation_preview
        ) {

          translationPreviewBox.style.display =
            "block";

          translationPreview.textContent =
            status.job.translation_preview;

        }


        progressBar.style.width =
          currentProgress +
          "%";

        progressPercent.textContent =
          currentProgress +
          "%";


        if (
          status.job.status ===
          "completed"
        ) {

          completed = true;


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


          const downloadUrl =
            getDownloadUrl(
              jobId
            );


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
                downloadUrl;

            };


          statusBox.appendChild(
            downloadButton
          );


          alert(
            "Translation completed successfully!"
          );

        }


        if (
          status.job.status ===
          "failed"
        ) {

          completed = true;


          throw new Error(
            status.job.error_message ||
            "Translation failed."
          );

        }

        if (
          status.job.status ===
          "cancelled"
        ) {

          completed = true;

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

          cancelBtn.textContent =
            "Translation Cancelled";

          cancelBtn.disabled =
            true;

          cancelBtn.style.background =
            "#64748b";

          break;

        }

      }


    } catch (error) {

      jobStatus.textContent =
        "Translation failed";


      progressText.textContent =
        error.message;


      progressBar.style.width =
        "0%";


      etaText.textContent =
        "ETA: Failed";

      speedText.textContent =
        "Speed: Failed";

      alert(
        error.message
      );

      } finally {

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

          translateBtn.disabled =
            false;

          translateBtn.style.opacity =
            "1";

          translateBtn.style.cursor =
            "pointer";

          translateBtn.textContent =
            "Start Translation";

          cancelBtn.style.display =
            "none";

          cancelBtn.disabled =
            false;

          cancelBtn.textContent =
            "Cancel Translation";

          cancelBtn.style.background =
            "#dc2626";

      }
  
  }
);
