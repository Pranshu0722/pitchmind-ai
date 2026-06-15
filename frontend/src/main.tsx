import React from "react";
import ReactDOM from "react-dom/client";
import "./styles/globals.css";

// Phase 3: Router + QueryClient provider added here
// For now render a placeholder shell

function App() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-950">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-brand-500">PitchMind AI</h1>
        <p className="mt-2 text-gray-400">Multi-Agent Football Intelligence Platform</p>
        <p className="mt-4 text-sm text-gray-500">Phase 1 scaffold — Phase 3 builds the full UI</p>
      </div>
    </div>
  );
}

const root = document.getElementById("root");
if (!root) throw new Error("Root element not found");

ReactDOM.createRoot(root).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
