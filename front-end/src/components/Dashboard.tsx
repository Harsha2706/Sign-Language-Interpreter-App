import { useState, useRef } from "react";
import CameraComponent from "./CameraComponent";
import { useStore } from "../store/useStore";
import { useSpeech } from "../hooks/useSpeech";
import "./Dashboard.css";

type ActiveMode = "idle" | "detection" | "collect";

const Dashboard = () => {
  const [mode, setActiveMode] = useState<ActiveMode>("idle");
  const [collectedFrames, setCollectedFrames] = useState(0);
  const [collectedDatasets, setCollectedDatasets] = useState<number[][][]>([]);
  const [downloadReady, setDownloadReady] = useState(false);
  const frameBuffer = useRef<number[][]>([]);

  const { label, confidence } = useStore();
  const { speak } = useSpeech();

  /* ── Detection ── */
  const startDetection = () => {
    setActiveMode("detection");
    setDownloadReady(false);
  };
  const stopDetection = () => setActiveMode("idle");

  /* ── Collect Dataset ── */
  const startCollect = () => {
    setCollectedFrames(0);
    frameBuffer.current = [];
    setCollectedDatasets([]);
    setDownloadReady(false);
    setActiveMode("collect");
  };
  const stopCollect = () => {
    setActiveMode("idle");
    if (frameBuffer.current.length > 0) {
      setCollectedDatasets((prev) => [...prev, [...frameBuffer.current]]);
      setDownloadReady(true);
    }
  };

  const handleFrame = (sequence: number[][]) => {
    frameBuffer.current.push(...sequence);
    setCollectedFrames((n) => n + sequence.length);
  };

  const downloadDataset = () => {
    const allData =
      collectedDatasets.length > 0
        ? collectedDatasets
        : frameBuffer.current.length > 0
        ? [frameBuffer.current]
        : [];
    const blob = new Blob([JSON.stringify(allData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `sign-dataset-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  const isDetecting = mode === "detection";
  const isCollecting = mode === "collect";
  const isActive = mode !== "idle";

  return (
    <div className="dash">
      {/* ── Hero ── */}
      <section className="dash-hero">
        <h1 className="dash-title">
          <span className="dash-title-accent">Sign Language</span> Interpreter
        </h1>
      </section>

      {/* ── Main Layout ── */}
      <div className="dash-layout">
        {/* ── Camera Panel ── */}
        <div className="dash-camera-panel">
          <CameraComponent
            active={isActive}
            mode={isDetecting ? "detection" : "collect"}
            onFrame={handleFrame}
          />
          {/* Prediction overlay (only in detection mode) */}
          {isDetecting && label && (
            <div className="prediction-overlay">
              <span className="pred-label">{label}</span>
              <span className="pred-conf">{(confidence * 100).toFixed(0)}%</span>
            </div>
          )}
          {/* Frame counter (collect mode) */}
          {isCollecting && (
            <div className="frame-counter">
              <span className="frame-icon">⏺</span>
              <span>{collectedFrames} keypoints captured</span>
            </div>
          )}
        </div>

        {/* ── Controls Panel ── */}
        <div className="dash-controls-panel">

          {/* Detection Card */}
          <div className={`feature-card ${isDetecting ? "feature-card--active" : ""}`}>
            <div className="feature-card-icon detect-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <path d="M23 7 16 12 23 17V7z" />
                <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
              </svg>
            </div>
            <h2 className="feature-card-title">Camera Detection</h2>
            <p className="feature-card-desc">
              Activate your webcam and get real‑time sign language predictions streamed from the AI backend.
            </p>

            {isDetecting && label && (
              <div className="live-prediction">
                <div className="live-prediction-label">{label}</div>
                <div className="confidence-bar-wrap">
                  <div
                    className="confidence-bar-fill"
                    style={{ width: `${(confidence * 100).toFixed(0)}%` }}
                  />
                </div>
                <span className="confidence-text">{(confidence * 100).toFixed(1)}% confidence</span>
              </div>
            )}

            <div className="feature-card-actions">
              {!isDetecting ? (
                <button
                  id="start-detection-btn"
                  className="btn btn-primary"
                  onClick={startDetection}
                  disabled={isCollecting}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M8 5v14l11-7z" />
                  </svg>
                  Start Detection
                </button>
              ) : (
                <>
                  <button
                    id="stop-detection-btn"
                    className="btn btn-danger"
                    onClick={stopDetection}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                      <rect x="6" y="6" width="12" height="12" rx="1" />
                    </svg>
                    Stop Detection
                  </button>
                  {label && (
                    <button
                      id="speak-btn"
                      className="btn btn-outline"
                      onClick={() => speak(label)}
                    >
                      🔊 Speak
                    </button>
                  )}
                </>
              )}
            </div>
          </div>

          {/* Divider */}
          <div className="card-divider" />

          {/* Dataset Collection Card */}
          <div className={`feature-card ${isCollecting ? "feature-card--active feature-card--collect" : ""}`}>
            <div className="feature-card-icon collect-icon">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                <circle cx="12" cy="12" r="10" />
                <circle cx="12" cy="12" r="3" fill="currentColor" stroke="none" />
              </svg>
            </div>
            <h2 className="feature-card-title">Collect Dataset</h2>
            <p className="feature-card-desc">
              Record your own sign gestures to build training data. Captured keypoint sequences can be exported as JSON.
            </p>

            {isCollecting && (
              <div className="collect-stats">
                <div className="collect-stat">
                  <span className="collect-stat-num">{collectedFrames}</span>
                  <span className="collect-stat-label">Keypoints</span>
                </div>
                <div className="collect-stat">
                  <span className="collect-stat-num">{Math.floor(collectedFrames / 30)}</span>
                  <span className="collect-stat-label">Sequences</span>
                </div>
              </div>
            )}

            {downloadReady && !isCollecting && (
              <div className="download-ready">
                ✅ {collectedDatasets.reduce((a, d) => a + d.length, 0)} keypoints collected &amp; ready
              </div>
            )}

            <div className="feature-card-actions">
              {!isCollecting ? (
                <>
                  <button
                    id="collect-dataset-btn"
                    className="btn btn-record"
                    onClick={startCollect}
                    disabled={isDetecting}
                  >
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                      <circle cx="12" cy="12" r="8" />
                    </svg>
                    Collect Dataset
                  </button>
                  {downloadReady && (
                    <button
                      id="download-dataset-btn"
                      className="btn btn-outline"
                      onClick={downloadDataset}
                    >
                      ⬇ Export JSON
                    </button>
                  )}
                </>
              ) : (
                <button
                  id="stop-collect-btn"
                  className="btn btn-danger"
                  onClick={stopCollect}
                >
                  <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
                    <rect x="6" y="6" width="12" height="12" rx="1" />
                  </svg>
                  Stop Recording
                </button>
              )}
            </div>
          </div>

          {/* Sign vocabulary quick ref */}
          <div className="sign-vocab">
            <h3 className="sign-vocab-title">Recognisable Signs</h3>
            <div className="sign-vocab-grid">
              {[
                "hello","yes","no","please","thank you","sorry","help",
                "good","bad","happy","sad","love","eat","drink","go","stop",
              ].map((s) => (
                <span key={s} className="sign-tag">{s}</span>
              ))}
              <span className="sign-tag sign-tag-more">+21 more</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
