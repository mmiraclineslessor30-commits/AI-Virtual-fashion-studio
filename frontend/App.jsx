import { useState } from "react";
import "./App.css";

function App() {
  const [personImage, setPersonImage] = useState(null);
  const [garmentImage, setGarmentImage] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleImage = (event, type) => {
    const file = event.target.files?.[0];

    if (!file) return;

    const imageUrl = URL.createObjectURL(file);

    if (type === "person") {
      setPersonImage(imageUrl);
    } else {
      setGarmentImage(imageUrl);
    }
  };

  const handleGenerate = async () => {
    if (!personImage || !garmentImage) {
      alert("Please upload both person and garment images.");
      return;
    }

    setLoading(true);
    setResult(null);

    /*
      Backend connection will be connected here.

      Backend:
      http://127.0.0.1:8000

      For now we show the professional processing state.
    */

    setTimeout(() => {
      setLoading(false);
      setResult({
        score: 88,
        color: 91,
        silhouette: 86,
        occasion: 89,
      });
    }, 2500);
  };

  return (
    <div className="app">

      {/* NAVIGATION */}

      <nav className="navbar">

        <div className="brand">
          <div className="brand-icon">✦</div>

          <span>
            AURA<span>STUDIO</span>
          </span>
        </div>

        <div className="nav-links">
          <a href="#studio">Studio</a>
          <a href="#intelligence">Intelligence</a>
          <a href="#technology">Technology</a>
        </div>

        <div className="status">
          <span></span>
          AI ENGINE ONLINE
        </div>

      </nav>


      {/* HERO */}

      <section className="hero">

        <div className="hero-content">

          <div className="eyebrow">
            AI-POWERED FASHION INTELLIGENCE
          </div>

          <h1>
            Your style.
            <br />
            <span>Reimagined.</span>
          </h1>

          <p>
            Experience intelligent virtual try-on, garment analysis,
            personalised styling and fashion intelligence in one
            sophisticated creative studio.
          </p>

          <a href="#studio" className="primary-button">
            ENTER THE STUDIO →
          </a>

        </div>


        <div className="hero-orbit">

          <div className="orbit orbit-one"></div>
          <div className="orbit orbit-two"></div>

          <div className="hero-card">

            <div className="hero-card-label">
              AURA / AI-01
            </div>

            <div>
              <div className="hero-card-line"></div>

              <div className="hero-card-title">
                Intelligent
                <br />
                Fashion
                <br />
                Experience
              </div>
            </div>

            <div className="hero-card-footer">
              <span>● ONLINE</span>
              <span>VISION ENGINE</span>
            </div>

          </div>

        </div>

      </section>


      {/* METRICS */}

      <section className="metrics">

        <div>
          <strong>01</strong>
          VIRTUAL TRY-ON
        </div>

        <div>
          <strong>02</strong>
          STYLE ANALYSIS
        </div>

        <div>
          <strong>03</strong>
          COLOR INTELLIGENCE
        </div>

        <div>
          <strong>04</strong>
          SMART STYLING
        </div>

      </section>


      {/* STUDIO */}

      <section className="studio-section" id="studio">

        <div className="section-heading">

          <div>
            <div className="section-number">
              01 — VIRTUAL STUDIO
            </div>

            <h2>
              Build your
              <br />
              <span>look.</span>
            </h2>
          </div>

          <p>
            Upload a person image and a garment image.
            Our computer vision pipeline prepares the inputs
            for intelligent virtual styling.
          </p>

        </div>


        <div className="studio-grid">

          {/* PERSON */}

          <div className="panel">

            <div className="panel-header">
              <span>01 / PERSON</span>
              <small>IMAGE INPUT</small>
            </div>

            <label className="upload-box">

              <input
                type="file"
                accept="image/*"
                onChange={(event) =>
                  handleImage(event, "person")
                }
              />

              {personImage ? (
                <img
                  src={personImage}
                  alt="Person preview"
                />
              ) : (
                <>
                  <div className="upload-icon">
                    ↑
                  </div>

                  <strong>
                    Upload Person Image
                  </strong>

                  <span>
                    JPG / PNG / WEBP
                  </span>
                </>
              )}

            </label>

          </div>


          {/* GARMENT */}

          <div className="panel">

            <div className="panel-header">
              <span>02 / GARMENT</span>
              <small>IMAGE INPUT</small>
            </div>

            <label className="upload-box">

              <input
                type="file"
                accept="image/*"
                onChange={(event) =>
                  handleImage(event, "garment")
                }
              />

              {garmentImage ? (
                <img
                  src={garmentImage}
                  alt="Garment preview"
                />
              ) : (
                <>
                  <div className="upload-icon">
                    ↑
                  </div>

                  <strong>
                    Upload Garment Image
                  </strong>

                  <span>
                    JPG / PNG / WEBP
                  </span>
                </>
              )}

            </label>

          </div>

        </div>


        {/* CONFIGURATION */}

        <div className="configuration">

          <div className="config-title">
            <span>STYLE CONFIGURATION</span>
            <small>AI PARAMETERS</small>
          </div>

          <div className="input-grid">

            <label>
              HEIGHT
              <input
                type="number"
                placeholder="170"
              />
            </label>

            <label>
              FIT
              <select defaultValue="Regular">
                <option>Regular</option>
                <option>Relaxed</option>
                <option>Slim</option>
                <option>Oversized</option>
              </select>
            </label>

            <label>
              OCCASION
              <select defaultValue="Casual">
                <option>Casual</option>
                <option>College</option>
                <option>Office</option>
                <option>Party</option>
                <option>Wedding</option>
              </select>
            </label>

            <label>
              STYLE
              <select defaultValue="Modern">
                <option>Modern</option>
                <option>Minimal</option>
                <option>Streetwear</option>
                <option>Classic</option>
                <option>Luxury</option>
              </select>
            </label>

            <label>
              SILHOUETTE
              <select defaultValue="Balanced">
                <option>Balanced</option>
                <option>Rectangle</option>
                <option>Triangle</option>
                <option>Inverted Triangle</option>
                <option>Hourglass</option>
              </select>
            </label>

            <label>
              SKIN TONE
              <select defaultValue="Auto">
                <option>Auto</option>
                <option>Fair</option>
                <option>Medium</option>
                <option>Deep</option>
              </select>
            </label>

          </div>

          <label className="garment-description">
            GARMENT DESCRIPTION

            <input
              type="text"
              placeholder="Example: oversized beige linen shirt"
            />

          </label>


          <button
            className="generate-button"
            onClick={handleGenerate}
            disabled={loading}
          >
            {loading
              ? "ANALYSING YOUR LOOK..."
              : "GENERATE AI LOOK →"}
          </button>

        </div>

      </section>


      {/* PROCESSING */}

      {loading && (

        <section className="processing">

          <div className="loader"></div>

          <span>
            AURA VISION ENGINE
          </span>

          <h2>
            Analysing your style...
          </h2>

          <p>
            Validating image · Understanding garment ·
            Building fashion profile
          </p>

        </section>

      )}


      {/* RESULTS */}

      {result && (

        <section className="results" id="intelligence">

          <div className="section-heading">

            <div>

              <div className="section-number">
                02 — STYLE INTELLIGENCE
              </div>

              <h2>
                Your look,
                <br />
                <span>decoded.</span>
              </h2>

            </div>

            <p>
              AI-generated style compatibility metrics
              based on the selected garment and profile.
            </p>

          </div>


          <div className="result-grid">

            <div className="result-image-card">

              <span className="result-label">
                VIRTUAL LOOK
              </span>

              {personImage && (
                <img
                  src={personImage}
                  alt="Virtual styling result"
                />
              )}

            </div>


            <div className="intelligence-card">

              <span className="result-label">
                OVERALL COMPATIBILITY
              </span>

              <div className="score-main">
                <strong>{result.score}</strong>
                <span>/100</span>
              </div>

              <p>
                Strong visual compatibility detected.
              </p>

              <div className="score-row">
                <span>Color Harmony</span>
                <strong>{result.color}/100</strong>
              </div>

              <div className="score-row">
                <span>Silhouette</span>
                <strong>{result.silhouette}/100</strong>
              </div>

              <div className="score-row">
                <span>Occasion Fit</span>
                <strong>{result.occasion}/100</strong>
              </div>

            </div>

          </div>

        </section>

      )}


      {/* TECHNOLOGY */}

      <section
        className="studio-section"
        id="technology"
      >

        <div className="section-heading">

          <div>

            <div className="section-number">
              03 — TECHNOLOGY
            </div>

            <h2>
              Built like a
              <br />
              <span>flagship ML system.</span>
            </h2>

          </div>

          <p>
            A modular computer vision architecture designed
            for image validation, garment intelligence,
            virtual try-on and personalised fashion analysis.
          </p>

        </div>

        <div className="studio-grid">

          <div className="panel">
            <div className="panel-header">
              <span>COMPUTER VISION</span>
              <small>01</small>
            </div>

            <p>
              Image validation, preprocessing, garment
              understanding and visual feature extraction.
            </p>
          </div>

          <div className="panel">
            <div className="panel-header">
              <span>AI STYLE ENGINE</span>
              <small>02</small>
            </div>

            <p>
              Body profile, color harmony, silhouette
              compatibility and occasion-aware styling.
            </p>
          </div>

          <div className="panel">
            <div className="panel-header">
              <span>VIRTUAL TRY-ON</span>
              <small>03</small>
            </div>

            <p>
              Generative virtual garment transformation
              pipeline powered by modern deep learning.
            </p>
          </div>

          <div className="panel">
            <div className="panel-header">
              <span>SMART RECOMMENDATIONS</span>
              <small>04</small>
            </div>

            <p>
              Accessories, complementary pieces and
              contextual outfit recommendations.
            </p>
          </div>

        </div>

      </section>


      {/* FOOTER */}

      <footer>

        <div>

          <strong>
            AURA<span>STUDIO</span>
          </strong>

          <p>
            AI Virtual Fashion Intelligence Platform
          </p>

        </div>

        <div>
          Python · Computer Vision · Deep Learning · React
        </div>

      </footer>

    </div>
  );
}

export default App;