import os
import cv2
import numpy as np
import mediapipe as mp

# --- CONFIG ---
VIDEO_DIR = r"F:\harsha\sign language\dataset\WLASL40_raw"
KEYPOINT_DIR = r"F:\harsha\sign language\dataset\WLASL40_keypoints"
FIXED_SEQ_LENGTH = 30  # number of frames per video
os.makedirs(KEYPOINT_DIR, exist_ok=True)

mp_holistic = mp.solutions.holistic

# --- FUNCTIONS ---

def extract_keypoints_from_frame(results):
    """Flatten all landmarks into a single 1D array."""
    pose = np.zeros(33*4)
    lh = np.zeros(21*3)
    rh = np.zeros(21*3)
    face = np.zeros(468*3)

    if results.pose_landmarks:
        pose = np.array([[lm.x, lm.y, lm.z, lm.visibility] 
                         for lm in results.pose_landmarks.landmark]).flatten()
    if results.left_hand_landmarks:
        lh = np.array([[lm.x, lm.y, lm.z] 
                       for lm in results.left_hand_landmarks.landmark]).flatten()
    if results.right_hand_landmarks:
        rh = np.array([[lm.x, lm.y, lm.z] 
                       for lm in results.right_hand_landmarks.landmark]).flatten()
    if results.face_landmarks:
        face = np.array([[lm.x, lm.y, lm.z] 
                         for lm in results.face_landmarks.landmark]).flatten()

    return np.concatenate([pose, lh, rh, face])

def normalize_keypoints(keypoints):
    """Center around pose midpoint and scale to 0-1."""
    if keypoints.size == 0:
        return keypoints
    # Use first 3 values of pose (x, y, z) as reference center
    center_x, center_y, center_z = keypoints[0], keypoints[1], keypoints[2]
    keypoints[::4] -= center_x  # pose x
    keypoints[1::4] -= center_y  # pose y
    keypoints[2::4] -= center_z  # pose z
    # scale all values between -1 and 1
    max_val = np.max(np.abs(keypoints))
    if max_val > 0:
        keypoints /= max_val
    return keypoints

def process_video(video_path, seq_length=FIXED_SEQ_LENGTH):
    """Extract, normalize, and standardize video keypoints."""
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"[WARNING] Cannot open video {video_path}, skipping.")
        return None

    keypoints_seq = []
    with mp_holistic.Holistic(static_image_mode=False,
                              min_detection_confidence=0.5,
                              min_tracking_confidence=0.5) as holistic:
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            results = holistic.process(frame_rgb)
            kp = extract_keypoints_from_frame(results)
            kp = normalize_keypoints(kp)
            keypoints_seq.append(kp)

    cap.release()
    if len(keypoints_seq) == 0:
        return None

    # --- Sequence Standardization ---
    keypoints_seq = np.array(keypoints_seq)
    if len(keypoints_seq) < seq_length:
        # pad with zeros
        pad_len = seq_length - len(keypoints_seq)
        keypoints_seq = np.pad(keypoints_seq, ((0, pad_len), (0,0)), 'constant')
    elif len(keypoints_seq) > seq_length:
        # uniform resampling
        idxs = np.linspace(0, len(keypoints_seq)-1, seq_length).astype(int)
        keypoints_seq = keypoints_seq[idxs]

    return keypoints_seq

# --- MAIN LOOP ---
for word in os.listdir(VIDEO_DIR):
    word_path = os.path.join(VIDEO_DIR, word)
    if not os.path.isdir(word_path):
        continue

    word_keypoint_dir = os.path.join(KEYPOINT_DIR, word)
    os.makedirs(word_keypoint_dir, exist_ok=True)

    for video in os.listdir(word_path):
        if not video.endswith(".mp4"):
            continue

        video_path = os.path.join(word_path, video)
        out_path = os.path.join(word_keypoint_dir, video.replace('.mp4', '.npy'))

        if os.path.exists(out_path):
            continue  # skip already processed

        try:
            keypoints_seq = process_video(video_path)
            if keypoints_seq is None:
                print(f"[SKIPPED] {video_path}")
                continue
            np.save(out_path, keypoints_seq)
            print(f"[SUCCESS] Saved keypoints for {video_path}")
        except Exception as e:
            print(f"[ERROR] Failed processing {video_path}: {e}")
            continue

print("✅ Preprocessing complete! All usable videos processed.")