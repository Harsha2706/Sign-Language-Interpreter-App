# src/dataset.py
import os
import numpy as np
import torch
from torch.utils.data import Dataset

class SignDataset(Dataset):
    def __init__(self, keypoint_dir, seq_length=30):
        self.keypoint_dir = keypoint_dir
        self.seq_length = seq_length
        self.word2idx = {word:i for i, word in enumerate(os.listdir(keypoint_dir))}
        self.samples = []

        for word in os.listdir(keypoint_dir):
            word_path = os.path.join(keypoint_dir, word)
            if not os.path.isdir(word_path):
                continue
            for npy_file in os.listdir(word_path):
                if npy_file.endswith(".npy"):
                    self.samples.append((os.path.join(word_path, npy_file), word))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, word = self.samples[idx]
        seq = np.load(path).astype(np.float32)
        # Sequence standardization
        if len(seq) < self.seq_length:
            pad_len = self.seq_length - len(seq)
            seq = np.pad(seq, ((0, pad_len), (0,0)), 'constant')
        elif len(seq) > self.seq_length:
            idxs = np.linspace(0, len(seq)-1, self.seq_length).astype(int)
            seq = seq[idxs]
        label = self.word2idx[word]
        return torch.tensor(seq), torch.tensor(label)