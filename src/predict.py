# src/predict.py
import os
import torch
import numpy as np
from model import SignLanguageModel
from dataset import SignDataset

# --- Config ---
KEYPOINT_DIR = r"../dataset/WLASL40_keypoints"
MODEL_PATH = r"../models/model.pt"
SEQ_LENGTH = 30

# --- Load dataset to get word mapping ---
dataset = SignDataset(KEYPOINT_DIR, seq_length=SEQ_LENGTH)
word2idx = dataset.word2idx
idx2word = {v: k for k, v in word2idx.items()}

# --- Find any sample .npy to get input_dim ---
sample_seq = None
for root, dirs, files in os.walk(KEYPOINT_DIR):
    for f in files:
        if f.endswith(".npy"):
            sample_seq = np.load(os.path.join(root, f))
            break
    if sample_seq is not None:
        break

if sample_seq is None:
    raise ValueError("No .npy files found in KEYPOINT_DIR")

input_dim = sample_seq.shape[1]
num_classes = len(word2idx)

# --- Load model ---
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SignLanguageModel(input_dim, num_classes).to(device)
model.load_state_dict(torch.load(MODEL_PATH, map_location=device))
model.eval()

# --- Prediction function ---
def predict(sequence):
    # Ensure sequence has the right length
    if sequence.shape[0] < SEQ_LENGTH:
        pad_len = SEQ_LENGTH - sequence.shape[0]
        sequence = np.pad(sequence, ((0, pad_len), (0,0)), 'constant')
    elif sequence.shape[0] > SEQ_LENGTH:
        idxs = np.linspace(0, sequence.shape[0]-1, SEQ_LENGTH).astype(int)
        sequence = sequence[idxs]

    seq_tensor = torch.tensor(sequence[np.newaxis, :, :], dtype=torch.float32).to(device)
    with torch.no_grad():
        log_probs = model(seq_tensor)
        probs = torch.exp(log_probs)
        conf, idx = torch.max(probs, dim=1)
        return idx2word[idx.item()], conf.item()

# --- Example: pick first available .npy automatically ---
example_path = None
for root, dirs, files in os.walk(KEYPOINT_DIR):
    for f in files:
        if f.endswith(".npy"):
            example_path = os.path.join(root, f)
            break
    if example_path:
        break

if example_path is None:
    raise ValueError("No .npy files found for prediction.")

sequence = np.load(example_path)
word, confidence = predict(sequence)
print(f"Predicted: {word}, Confidence: {confidence:.4f}")