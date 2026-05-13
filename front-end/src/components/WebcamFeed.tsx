import { useRef, useCallback } from "react";
import { useMediaPipe } from "../hooks/useMediaPipe";
import { useWebSocket } from "../hooks/useWebSocket";

const WebcamFeed = () => {
  const videoRef = useRef<HTMLVideoElement>(null);
  const { send } = useWebSocket();

  const handleResults = useCallback((sequence: number[][]) => {
    send(sequence);
  }, []);

  useMediaPipe(videoRef, handleResults);

  return (
    <div>
      <video ref={videoRef} autoPlay playsInline />
    </div>
  );
};

export default WebcamFeed;