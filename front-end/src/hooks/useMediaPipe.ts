import { useEffect, useRef } from "react";

export const useMediaPipe = (
  videoRef: React.RefObject<HTMLVideoElement | null>,
  onResults: (sequence: number[][]) => void,
  enabled: boolean = true
) => {
  const sequenceRef = useRef<number[][]>([]);

  const onResultsRef = useRef(onResults);
  onResultsRef.current = onResults;

  useEffect(() => {
    if (!enabled) return;

    let camera: any = null;
    let holistic: any = null;
    let active = true;

    const init = async () => {
      if (!videoRef.current) return;

      const video = videoRef.current;

      if (!(window as any).Holistic || !(window as any).Camera) {
        console.error("❌ MediaPipe not loaded");
        return;
      }

      let stream: MediaStream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
      } catch (err) {
        console.error("❌ Camera access denied", err);
        return;
      }

      if (!active) {
        stream.getTracks().forEach((t) => t.stop());
        return;
      }

      video.srcObject = stream;
      await video.play().catch(() => { });

      holistic = new (window as any).Holistic({
        locateFile: (file: string) =>
          `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}`,
      });

      holistic.setOptions({
        modelComplexity: 1,
        smoothLandmarks: true,
        refineFaceLandmarks: false, // important but not enough alone
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
      });

      holistic.onResults((results: any) => {
        if (!active) return;

        const keypoints = extractKeypoints(results);

        // ✅ MUST BE 258
        if (keypoints.length !== 258) {
          console.error("❌ Wrong keypoints length:", keypoints.length);
          return;
        }

        sequenceRef.current.push(keypoints);

        if (sequenceRef.current.length === 30) {
          onResultsRef.current([...sequenceRef.current]);
          sequenceRef.current = [];
        }
      });

      camera = new (window as any).Camera(video, {
        onFrame: async () => {
          if (!active || !holistic) return;
          await holistic.send({ image: video });
        },
        width: 640,
        height: 480,
      });

      camera.start();
      console.log("✅ MediaPipe camera started");
    };

    init();

    return () => {
      active = false;
      console.log("🛑 MediaPipe camera stopped");

      if (camera) camera.stop();
      if (holistic) holistic.close();

      if (videoRef.current?.srcObject) {
        const s = videoRef.current.srcObject as MediaStream;
        s.getTracks().forEach((t) => t.stop());
        videoRef.current.srcObject = null;
      }

      sequenceRef.current = [];
    };
  }, [enabled]);
};


// 🔥 FIXED KEYPOINT EXTRACTION (258 ONLY)
function extractKeypoints(results: any): number[] {
  // ✅ ONLY pose + hands (NO FACE)

  const pose: number[] = results.poseLandmarks
    ? results.poseLandmarks.flatMap((p: any) => [p.x, p.y, p.z, p.visibility])
    : new Array(33 * 4).fill(0); // 132

  const leftHand: number[] = results.leftHandLandmarks
    ? results.leftHandLandmarks.flatMap((p: any) => [p.x, p.y, p.z])
    : new Array(21 * 3).fill(0); // 63

  const rightHand: number[] = results.rightHandLandmarks
    ? results.rightHandLandmarks.flatMap((p: any) => [p.x, p.y, p.z])
    : new Array(21 * 3).fill(0); // 63

  // ✅ TOTAL = 258
  const all = [...pose, ...leftHand, ...rightHand];

  // ── NORMALIZATION (UPDATED FOR 258) ──

  const lsX = all[44];
  const lsY = all[45];
  const rsX = all[48];
  const rsY = all[49];

  const centerX = (lsX + rsX) / 2;
  const centerY = (lsY + rsY) / 2;

  // Pose (stride 4)
  for (let i = 0; i < 33 * 4; i += 4) {
    all[i] -= centerX;
    all[i + 1] -= centerY;
  }

  // Hands only now (NO FACE anymore)
  for (let i = 33 * 4; i < all.length; i += 3) {
    all[i] -= centerX;
    all[i + 1] -= centerY;
  }

  // Scale
  let maxVal = 0;
  for (let i = 0; i < all.length; i++) {
    if (Math.abs(all[i]) > maxVal) maxVal = Math.abs(all[i]);
  }

  if (maxVal > 0) {
    for (let i = 0; i < all.length; i++) {
      all[i] /= maxVal;
    }
  }

  return all;
}