import React from "react";
import ReactDOM from "react-dom/client";

let App;

try {
  const module = await import("./App.jsx");
  App = module.default;
} catch (error) {
  document.getElementById("root").innerHTML = `
    <div style="
      padding: 30px;
      color: red;
      background: white;
      font-family: Arial, sans-serif;
      white-space: pre-wrap;
    ">
      <h1>App Import Error</h1>
      <pre>${error.stack || error.message}</pre>
    </div>
  `;

  throw error;
}

ReactDOM.createRoot(
  document.getElementById("root")
).render(
  <App />
);
