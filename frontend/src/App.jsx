import { useState } from "react";

function App() {
  const [file, setFile] = useState(null);
  const [batchSize, setBatchSize] = useState(100);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files?.[0];

    if (!selectedFile) {
      return;
    }

    if (!selectedFile.name.toLowerCase().endsWith(".srt")) {
      alert("Please select a valid SRT file.");
      return;
    }

    setFile(selectedFile);
  };

  const handleDrop = (event) => {
    event.preventDefault();

    const droppedFile = event.dataTransfer.files?.[0];

    if (!droppedFile) {
      return;
    }

    if (!droppedFile.name.toLowerCase().endsWith(".srt")) {
      alert("Please drop a valid SRT file.");
      return;
    }

    setFile(droppedFile);
  };

  const handleDragOver = (event) => {
    event.preventDefault();
  };

  const removeFile = () => {
    setFile(null);
  };

  return (
    <main className="app-container">
      <section className="translator-card">

        <div className="brand-section">
          <div className="brand-icon">✦</div>

          <h1>Ultimate AI Translator</h1>

          <p>
            Translate your SRT subtitles into natural
            Indian Hinglish with AI.
          </p>
        </div>

        <div
          className="upload-area"
          onDrop={handleDrop}
          onDragOver={handleDragOver}
        >
          {!file ? (
            <>
              <div className="upload-icon">↑</div>

              <h2>Upload your SRT file</h2>

              <p>
                Drag & drop your subtitle file here
                or choose a file from your device.
              </p>

              <label className="browse-button">
                Browse SRT File

                <input
                  type="file"
                  accept=".srt"
                  onChange={handleFileChange}
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
                <strong>{file.name}</strong>

                <span>
                  {(file.size / 1024).toFixed(1)} KB
                </span>
              </div>

              <button
                className="remove-button"
                onClick={removeFile}
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
              <span>🌐</span>
              <span>Auto Detect</span>
            </div>
          </div>

          <div className="setting-box">
            <label>
              Target Language
            </label>

            <div className="setting-value">
              <span>🇮🇳</span>
              <span>Hinglish</span>
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
            onChange={(event) =>
              setBatchSize(
                Number(event.target.value)
              )
            }
          />

          <div className="range-labels">
            <span>1</span>
            <span>500</span>
          </div>

        </div>

        <button
          className="translate-button"
          disabled={!file}
        >
          ✨ Start Translation
        </button>

        {!file && (
          <p className="helper-text">
            Upload an SRT file to start translation.
          </p>
        )}

      </section>

      <footer>
        Powered by AI · Built for subtitle creators
      </footer>
    </main>
  );
}

export default App;
