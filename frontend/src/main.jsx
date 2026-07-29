import React from "react";
import ReactDOM from "react-dom/client";

import App from "./App.jsx";

ReactDOM.createRoot(
  document.getElementById("root")
).render(
  <div
    style={{
      minHeight: "100vh",
      background: "white",
      color: "black",
      padding: "50px",
      fontSize: "30px",
    }}
  >
    <div>App Import Test</div>

    <div style={{ marginTop: "20px" }}>
      {typeof App}
    </div>
  </div>
);
