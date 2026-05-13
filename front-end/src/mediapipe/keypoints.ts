// src/mediapipe/keypoints.ts
export const extractKeypoints = (results: any) => {
  const pose = results.poseLandmarks?.flat() ?? [];
  const face = results.faceLandmarks?.flat() ?? [];
  const leftHand = results.leftHandLandmarks?.flat() ?? [];
  const rightHand = results.rightHandLandmarks?.flat() ?? [];

  return [...pose, ...face, ...leftHand, ...rightHand];
};