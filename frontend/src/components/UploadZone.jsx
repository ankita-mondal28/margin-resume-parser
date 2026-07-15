import { useRef, useState } from "react";

const ACCEPTED_EXTENSIONS = [".pdf", ".docx", ".png", ".jpg", ".jpeg"];
const MAX_SIZE_MB = 8;

function getExtension(filename) {
  const idx = filename.lastIndexOf(".");
  return idx === -1 ? "" : filename.slice(idx).toLowerCase();
}

export default function UploadZone({ onSubmit, error, setError }) {
  const [file, setFile] = useState(null);
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef(null);

  function validateAndSetFile(candidate) {
    setError(null);
    if (!candidate) return;

    const ext = getExtension(candidate.name);
    if (!ACCEPTED_EXTENSIONS.includes(ext)) {
      setError(`"${ext || "unknown"}" isn't supported. Try a PDF, DOCX, or image (PNG/JPG).`);
      return;
    }
    if (candidate.size > MAX_SIZE_MB * 1024 * 1024) {
      setError(`That file is a bit large — please keep it under ${MAX_SIZE_MB}MB.`);
      return;
    }
    setFile(candidate);
  }

  function handleDrop(e) {
    e.preventDefault();
    setDragging(false);
    const dropped = e.dataTransfer.files?.[0];
    validateAndSetFile(dropped);
  }

  return (
    <div className="upload-stage">
      <div className="upload-intro">
        <h1>Let's read your resume.</h1>
        <p>Drop it in like you're handing it to a friend — we'll mark it up with notes.</p>
      </div>

      <div
        className={`paper-card dropzone ${dragging ? "dragging" : ""}`}
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={handleDrop}
        role="button"
        tabIndex={0}
        onKeyDown={(e) => {
          if (e.key === "Enter" || e.key === " ") inputRef.current?.click();
        }}
        aria-label="Upload your resume"
      >
        <div className="dropzone-icon" aria-hidden="true">
          📎
        </div>
        <h2>Drop your resume here</h2>
        <p>or click to browse your files</p>
        <div className="file-types">PDF · DOCX · PNG · JPG — up to {MAX_SIZE_MB}MB</div>
        <input
          ref={inputRef}
          type="file"
          className="file-input-hidden"
          accept={ACCEPTED_EXTENSIONS.join(",")}
          onChange={(e) => validateAndSetFile(e.target.files?.[0])}
        />
      </div>

      {file && (
        <div className="selected-file-bar">
          <span className="selected-file-name">📄 {file.name}</span>
          <button className="btn btn-ghost" onClick={() => setFile(null)}>
            remove
          </button>
        </div>
      )}

      {error && (
        <div className="error-note" role="alert">
          <span aria-hidden="true">✎</span>
          <span>{error}</span>
        </div>
      )}

      <div style={{ textAlign: "center", marginTop: 22 }}>
        <button className="btn btn-primary" disabled={!file} onClick={() => onSubmit(file)}>
          Read my resume →
        </button>
      </div>
    </div>
  );
}
