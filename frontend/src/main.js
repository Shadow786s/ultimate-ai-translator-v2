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
    <p>Frontend is working successfully.</p>

    <div style="
      margin:40px auto;
      max-width:500px;
      padding:30px;
      background:#1e293b;
      border-radius:20px;
    ">
      <h2>Upload SRT File</h2>
      <input type="file" accept=".srt" />
      <br/><br/>
      <button>
        Start Translation
      </button>
    </div>
  </div>
`;
