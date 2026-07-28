import { useEffect, useState } from "react";

import {
  uploadSrt,
  getJobStatus,
  getDownloadUrl,
} from "./api.js";


function App() {

  const [file, setFile] = useState(null);

  const [batchSize, setBatchSize] =
    useState(100);

  const [jobId, setJobId] =
    useState(null);

  const [job, setJob] =
    useState(null);

  const [loading, setLoading] =
    useState(false);

  const [error, setError] =
    useState("");


  const handleFileChange = (event) => {

    const selectedFile =
      event.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    if (
      !selectedFile.name
        .toLowerCase()
        .endsWith(".srt")
    ) {

      setError(
        "Please select a valid SRT file."
      );

      return;
    }

    setError("");

    setFile(selectedFile);
  };


  const handleDrop = (event) => {

    event.preventDefault();

    const droppedFile =
      event.dataTransfer.files?.[0];

    if (!droppedFile) {
      return;
    }

    if (
      !droppedFile.name
        .toLowerCase()
        .endsWith(".srt")
    ) {

      setError(
        "Please drop a valid SRT file."
      );

      return;
    }

    setError("");

    setFile(droppedFile);
  };


  const handleDragOver = (event) => {

    event.preventDefault();

  };


  const removeFile = () => {

    setFile(null);

    setJob(null);

    setJobId(null);

    setError("");

  };


  const handleTranslate = async () => {

    if (!file) {

      setError(
        "Please select an SRT file first."
      );

      return;
    }

    try {

      setLoading(true);

      setError("");

      setJob(null);

      setJobId(null);


      const result =
        await uploadSrt(
          file,
          batchSize
        );


      setJobId(
        result.job_id
      );

    } catch (error) {

      setError(
        error.message ||
        "Failed to start translation."
      );

    } finally {

      setLoading(false);

    }

  };


  useEffect(() => {

    if (!jobId) {
      return;
    }


    let intervalId;


    const checkStatus =
      async () => {

        try {

          const result =
            await getJobStatus(
              jobId
            );

          setJob(
            result.job
          );


          if (
            result.job.status ===
              "completed" ||
            result.job.status ===
              "failed"
          ) {

            clearInterval(
              intervalId
            );

          }

        } catch (error) {

          setError(
            error.message ||
            "Failed to get job status."
          );

          clearInterval(
            intervalId
          );

        }

      };


    checkStatus();


    intervalId =
      setInterval(
        checkStatus,
        2000
      );


    return () => {

      clearInterval(
        intervalId
      );

    };

  }, [jobId]);


  return (

    <main className="app-container">

      <section className="translator-card">


        <div className="brand-section">

          <div className="brand-icon">
            ✦
          </div>

          <h1>
            Ultimate AI Translator
          </h1>

          <p>
            Translate your SRT subtitles
            into natural Indian Hinglish
            with AI.
          </p>

        </div>


        <div
          className="upload-area"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >

          {!file ? (

            <>

              <div className="upload-icon">
                ↑
              </div>

              <h2>
                Upload your SRT file
              </h2>

              <p>
                Drag & drop your subtitle
                file here or choose a file
                from your device.
              </p>


              <label className="browse-button">

                Browse SRT File

                <input
                  type="file"
                  accept=".srt"
                  onChange={
                    handleFileChange
                  }
                  hidden
                />

              </label>

            </>

          ) : (

            <div className="selected-file">

              <div className="file-icon">
                SRT
              </div>


              <div className="file-details">

                <strong>
                  {file.name}
                </strong>

                <span>
                  {(
                    file.size / 1024
                  ).toFixed(1)}
                  {" KB"}
                </span>

              </div>


              <button
                className="remove-button"
                onClick={
                  removeFile
                }
              >
                ×
              </button>

            </div>

          )}

        </div>


        <div className="settings-grid">


          <div className="setting-box">

            <label>
              Source Language
            </label>

            <div className="setting-value">

              <span>
                🌐
              </span>

              <span>
                {job?.source_language ||
                  "Auto Detect"}
              </span>

            </div>

          </div>


          <div className="setting-box">

            <label>
              Target Language
            </label>

            <div className="setting-value">

              <span>
                🇮🇳
              </span>

              <span>
                Hinglish
              </span>

            </div>

          </div>


        </div>


        <div className="batch-section">


          <div className="batch-header">

            <label>
              Batch Size
            </label>

            <span>
              {batchSize} subtitles
            </span>

          </div>


          <input
            type="range"
            min="1"
            max="500"
            value={batchSize}
            onChange={
              (event) =>
                setBatchSize(
                  Number(
                    event.target.value
                  )
                )
            }
          />


          <div className="range-labels">

            <span>
              1
            </span>

            <span>
              500
            </span>

          </div>

        </div>


        <button
          className="translate-button"
          disabled={
            !file ||
            loading ||
            job?.status ===
              "processing"
          }
          onClick={
            handleTranslate
          }
        >

          {loading
            ? "Uploading..."
            : job?.status ===
              "processing"
            ? "Translating..."
            : "✨ Start Translation"}

        </button>


        {error && (

          <p className="error-message">
            {error}
          </p>

        )}


        {job && (

          <div className="job-status">

            <div className="job-status-header">

              <strong>
                Translation Status
              </strong>

              <span>
                {job.status}
              </span>

            </div>


            <div className="progress-bar">

              <div
                className="progress-fill"
                style={{
                  width:
                    `${job.progress}%`,
                }}
              />

            </div>


            <div className="progress-info">

              <span>
                {job.completed_items}
                {" / "}
                {job.total_items}
                {" subtitles"}
              </span>

              <span>
                {job.progress}%
              </span>

            </div>


            {job.status ===
              "completed" && (

              <a
                className="download-button"
                href={
                  getDownloadUrl(
                    job.id
                  )
                }
              >
                📥 Download Translated SRT
              </a>

            )}


            {job.status ===
              "failed" && (

              <p className="error-message">

                {job.error_message ||
                  "Translation failed."}

              </p>

            )}

          </div>

        )}


      </section>


      <footer>
        Powered by AI · Built for subtitle creators
      </footer>

    </main>

  );

}


export default App;
