import os
import numpy as np
from config import SEQ_DIR

def normalize(seq):
    mean = np.mean(seq, axis=0)
    std = np.std(seq) + 1e-6
    return (seq - mean) / std

def normalize_data():
    print("Normalizing data...")

    for file in os.listdir(SEQ_DIR):
        data = np.load(os.path.join(SEQ_DIR, file))

        norm_data = np.array([normalize(seq) for seq in data])

        np.save(os.path.join(SEQ_DIR, file), norm_data)