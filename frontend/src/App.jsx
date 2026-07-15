import { useState } from "react";
import UploadZone from "./components/UploadZone.jsx";
import Loader from "./components/Loader.jsx";
import ResultsPaper from "./components/ResultsPaper.jsx";
import { parseResume } from "./api/client.js";

export default function App() {
  const [status, setStatus] = useState("idle"); // idle | loading | done | error
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  async function handleSubmit(file) {
    setStatus("loading");
    setError(null);
    try {
      const data = await parseResume(file);
      setResult(data);
      setStatus("done");
    } catch (err) {
      setError(err.message);
      setStatus("idle");
    }
  }

  function handleReset() {
    setResult(null);
    setError(null);
    setStatus("idle");
  }

  return (
    <div className="app-shell">
      <header className="app-header">
        <div className="brand">
          <span className="brand-mark">Margin</span>
        </div>
        <p className="brand-tagline">resume notes, written by hand — powered by AI underneath</p>
      </header>

      <main>
        {status === "loading" && <Loader />}

        {status !== "loading" && status !== "done" && (
          <UploadZone onSubmit={handleSubmit} error={error} setError={setError} />
        )}

        {status === "done" && result && <ResultsPaper data={result} onReset={handleReset} />}
      </main>

      <footer className="app-footer">made with a fountain pen and a language model</footer>
    </div>
  );
}
