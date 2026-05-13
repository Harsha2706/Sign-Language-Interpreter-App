// src/mediapipe/holistic.ts
import * as mpHolistic from "@mediapipe/holistic";
const Holistic = mpHolistic.Holistic;

import * as mpCamera from "@mediapipe/camera_utils";
const Camera = mpCamera.Camera;
export const createHolistic = (onResults: (results: any) => void) => {
  const holistic = new Holistic({
    locateFile: (file) =>
      `https://cdn.jsdelivr.net/npm/@mediapipe/holistic/${file}`,
  });

  holistic.setOptions({
    modelComplexity: 1,
    smoothLandmarks: true,
    refineFaceLandmarks: true,
  });

  holistic.onResults(onResults);

  return holistic;
};