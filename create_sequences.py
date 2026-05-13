import os
import numpy as np
from config import KP_DIR, SEQ_DIR, SEQ_LEN

def create_sequences():
    os.makedirs(SEQ_DIR, exist_ok=True)

    print("Creating sequences...")

    for file in os.listdir(KP_DIR):
        data = np.load(os.path.join(KP_DIR, file))

        sequences = []

        for i in range(len(data) - SEQ_LEN):
            sequences.append(data[i:i+SEQ_LEN])

        np.save(os.path.join(SEQ_DIR, file), sequences)