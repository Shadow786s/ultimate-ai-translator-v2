import { uploadSrt, getJobStatus } from "./api.js";

document.getElementById("root").innerHTML = `
  <div style="
    min-height:100vh;
    background:#0f172a;
    color:white;
    padding:50px;
    font-family:Arial;
    text-align:center;
  ">
    <h1>Ultimate AI Translator</h1>
    <p>Select your SRT file</p>

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

      <br><br>

      <p id="fileName">
        No file selected
      </p>

      <button id="translateBtn">
        Start Translation
      </button>

      <div id="statusBox" style="
        margin-top:30px;
        display:none;
      ">
        <p id="jobStatus">
          Starting...
        </p>

        <p id="progressText">
          Progress: 0%
        </p>
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

      translateBtn.textContent =
        "Uploading...";

      statusBox.style.display =
        "block";

      jobStatus.textContent =
        "Creating translation job...";

      progressText.textContent =
        "Progress: 0%";


      const result =
        await uploadSrt(
          fileInput.files[0],
          100
        );

      const jobId =
        result.job_id;


      jobStatus.textContent =
        "Translation started";

      progressText.textContent =
        "Progress: 0%";


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


        jobStatus.textContent =
          "Status: " +
          status.status;


        progressText.textContent =
          "Progress: " +
          status.progress +
          "%";


        if (
          status.status ===
          "completed"
        ) {

          completed = true;

          jobStatus.textContent =
            "Translation completed successfully!";

          progressText.textContent =
            "Progress: 100%";

          alert(
            "Translation completed successfully!"
          );

        }


        if (
          status.status ===
          "failed"
        ) {

          completed = true;

          throw new Error(
            status.error_message ||
            "Translation failed."
          );

        }

      }


    } catch (error) {

      jobStatus.textContent =
        "Translation failed";

      progressText.textContent =
        error.message;

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
