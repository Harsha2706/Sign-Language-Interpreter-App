import os
import cv2
import numpy as np
import mediapipe as mp
from config import FRAME_DIR, KP_DIR

mp_holistic = mp.solutions.holistic

def extract_keypoints(image, model):
    results = model.process(image)
    keypoints = []

    if results.pose_landmarks:
        for lm in results.pose_landmarks.landmark:
            keypoints.extend([lm.x, lm.y, lm.z])
    else:
        keypoints.extend([0]*33*3)

    if results.left_hand_landmarks:
        for lm in results.left_hand_landmarks.landmark:
            keypoints.extend([lm.x, lm.y, lm.z])
    else:
        keypoints.extend([0]*21*3)

    if results.right_hand_landmarks:
        for lm in results.right_hand_landmarks.landmark:
            keypoints.extend([lm.x, lm.y, lm.z])
    else:
        keypoints.extend([0]*21*3)

    return np.array(keypoints)

def process_keypoints():
    os.makedirs(KP_DIR, exist_ok=True)

    print("Extracting keypoints...")

    with mp_holistic.Holistic(static_image_mode=True) as holistic:
        for video in os.listdir(FRAME_DIR):
            video_path = os.path.join(FRAME_DIR, video)

            video_kp = []

            for frame in sorted(os.listdir(video_path)):
                img = cv2.imread(os.path.join(video_path, frame))
                if img is None:
                    continue

                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                kp = extract_keypoints(img, holistic)
                video_kp.append(kp)

            np.save(os.path.join(KP_DIR, video + ".npy"), video_kp)