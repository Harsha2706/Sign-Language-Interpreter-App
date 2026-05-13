import { useRef } from "react";
import { useMediaPipe } from "../hooks/useMediaPipe";
import { useWebSocket } from "../hooks/useWebSocket";
import "./CameraComponent.css";

type Props = {
  active: boolean;
  mode: "detection" | "collect";
  onFrame?: (keypoints: number[][]) => void;
};

const CameraComponent = ({ active, mode, onFrame }: Props) => {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const { send } = useWebSocket();

  // Keep refs to the latest props so the stable MediaPipe callback
  // always reads the current values — no stale closure bugs.
  const modeRef = useRef(mode);
  modeRef.current = mode;
  const onFrameRef = useRef(onFrame);
  onFrameRef.current = onFrame;
  const sendRef = useRef(send);
  sendRef.current = send;

  // Stable callback — identity never changes, reads fresh values from refs.
  const handleResults = (sequence: number[][]) => {
    if (modeRef.current === "detection") {
      sendRef.current(sequence);
    } else if (modeRef.current === "collect") {
      onFrameRef.current?.(sequence);
    }
  };

  // useMediaPipe owns the webcam stream. Pass `active` so it starts/stops on demand.
  // No second getUserMedia call here — that was the race condition bug.
  useMediaPipe(videoRef, handleResults, active);

  return (
    <div className={`camera-wrap ${active ? "camera-active" : "camera-idle"}`}>
      {active ? (
        <>
          <video
            id="camera-video"
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="camera-video"
          />
          <div className="camera-indicator">
            {mode === "detection" ? (
              <span className="badge badge-detect">● LIVE</span>
            ) : (
              <span className="badge badge-record">⏺ Recording…</span>
            )}
          </div>
        </>
      ) : (
        <div className="camera-placeholder">
          <svg
            width="56"
            height="56"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="1.2"
            strokeLinecap="round"
            strokeLinejoin="round"
          >
            <path d="M23 7 16 12 23 17V7z" />
            <rect x="1" y="5" width="15" height="14" rx="2" ry="2" />
          </svg>
          <p>Camera not started</p>
        </div>
      )}
    </div>
  );
};

export default CameraComponent;
