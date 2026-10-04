
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8001";

function App() {
  const [personFile, setPersonFile] = useState(null);
  const [garmentFile, setGarmentFile] = useState(null);
  const [personImage, setPersonImage] = useState("");
  const [garmentImage, setGarmentImage] = useState("");
  const [resultImage, setResultImage] = useState("");
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");

  function handlePersonUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setPersonFile(file);
    setPersonImage(URL.createObjectURL(file));
    setResultImage("");
    setError("");
  }

  function handleGarmentUpload(event) {
    const file = event.target.files?.[0];
    if (!file) return;

    setGarmentFile(file);
    setGarmentImage(URL.createObjectURL(file));
    setResultImage("");
    setError("");
  }

  async function generateLook() {
    if (!personFile || !garmentFile) {
      setError("Please upload both a person photo and a garment image.");
      return;
    }

    setProcessing(true);
    setError("");
    setResultImage("");

    try {
      const formData = new FormData();
      formData.append("person", personFile);
      formData.append("garment", garmentFile);

      const response = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || `Request failed (${response.status})`);
      }

      const inference = data.pipeline?.inference;
      const result = inference?.result;

      if (inference?.status !== "completed" || !result?.output_filename) {
        throw new Error(
          inference?.message ||
            result?.message ||
            "Try-on could not be completed. Please try again."
        );
      }

      setResultImage(
        result.output_url
          ? `${API_URL}${result.output_url}`
          : `${API_URL}/outputs/${result.output_filename}`
      );
    } catch (err) {
      console.error("AURA try-on error:", err);
      setError(
        err.message ||
          "Unable to connect to the backend. Check that the backend is running."
      );
    } finally {
      setProcessing(false);
    }
  }

  return (
    <div className="app">
      <header className="header">
        <div className="brand">AURA<span> STUDIO</span></div>
        <div className="header-tag">AI VIRTUAL FASHION STUDIO</div>
      </header>

      <main className="main-content">
        <section className="hero">
          <p className="eyebrow">YOUR STYLE, REIMAGINED</p>
          <h1>
            Try the look.
            <br />
            <span>Before you wear it.</span>
          </h1>
          <p className="subtitle">
            Upload your photo, choose a garment, and let AI visualize your
            next look.
          </p>
        </section>

        <section className="upload-grid">
          <div className="upload-card">
            <div className="card-heading">
              <span className="step-number">01</span>
              <div>
                <h2>Your Photo</h2>
                <p>Upload a clear, full-body photo</p>
              </div>
            </div>

            <label className="upload-area">
              {personImage ? (
                <img
                  className="image-preview"
                  src={personImage}
                  alt="Uploaded person"
                />
              ) : (
                <div className="upload-placeholder">
                  <span className="upload-icon">＋</span>
                  <strong>Upload your photo</strong>
                  <span>Click to browse · JPG or PNG</span>
                </div>
              )}
              <input
                type="file"
                accept="image/*"
                onChange={handlePersonUpload}
                hidden
              />
            </label>

            {personFile && (
              <p className="file-name">{personFile.name}</p>
            )}
          </div>

          <div className="upload-card">
            <div className="card-heading">
              <span className="step-number">02</span>
              <div>
                <h2>Your Garment</h2>
                <p>Choose the clothing you want to try</p>
              </div>
            </div>

            <label className="upload-area">
              {garmentImage ? (
                <img
                  className="image-preview"
                  src={garmentImage}
                  alt="Uploaded garment"
                />
              ) : (
                <div className="upload-placeholder">
                  <span className="upload-icon">＋</span>
                  <strong>Upload a garment</strong>
                  <span>Click to browse · JPG or PNG</span>
                </div>
              )}
              <input
                type="file"
                accept="image/*"
                onChange={handleGarmentUpload}
                hidden
              />
            </label>

            {garmentFile && (
              <p className="file-name">{garmentFile.name}</p>
            )}
          </div>
        </section>

        <button
          className="generate-button"
          onClick={generateLook}
          disabled={processing}
        >
          {processing ? "GENERATING YOUR LOOK..." : "GENERATE MY LOOK →"}
        </button>

        {processing && (
          <p className="status-message">
            AI is processing your images. This may take a few minutes.
          </p>
        )}

        {error && <div className="error-message">{error}</div>}

        {resultImage && (
          <section className="result-section">
            <p className="eyebrow">YOUR NEW LOOK</p>
            <h2>Here's your virtual try-on</h2>

            <div className="result-image-container">
              <img
                className="result-image"
                src={resultImage}
                alt="AI-generated virtual try-on result"
                onError={() =>
                  setError(
                    "The result image could not be loaded. Please try generating again."
                  )
                }
              />
            </div>

            <a
              className="download-button"
              href={resultImage}
              download="aura-virtual-tryon.png"
              target="_blank"
              rel="noreferrer"
            >
              VIEW / SAVE YOUR RESULT ↗
            </a>
          </section>
        )}

        <footer className="footer">
          <span>AURA STUDIO</span>
          <span>AI-POWERED VIRTUAL FASHION</span>
        </footer>
      </main>
    </div>
  );
}

export default App;