import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATA_DIR = os.path.join(BASE_DIR, "dataset")

VIDEO_DIR = os.path.join(DATA_DIR, "WLASL40_raw")
FRAME_DIR = os.path.join(DATA_DIR, "frames")
KP_DIR = os.path.join(DATA_DIR, "keypoints")
SEQ_DIR = os.path.join(DATA_DIR, "sequences")
FINAL_DIR = os.path.join(DATA_DIR, "final")

SEQ_LEN = 30