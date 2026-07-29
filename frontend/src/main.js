import { uploadSrt } from "./api.js";
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
    </div>
  </div>
`;

const fileInput =
  document.getElementById("fileInput");

const fileName =
  document.getElementById("fileName");

const translateBtn =
  document.getElementById("translateBtn");

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

      const result =
        await uploadSrt(
          fileInput.files[0],
          100
        );

      alert(
        "Job created successfully!\n\nJob ID: " +
        result.job_id
      );

    } catch (error) {

      alert(error.message);

    } finally {

      translateBtn.disabled = false;
      translateBtn.textContent =
        "Start Translation";

    }

  }
);
