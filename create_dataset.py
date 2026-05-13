import os
import json
import numpy as np
from config import SEQ_DIR, FINAL_DIR

def create_dataset():
    os.makedirs(FINAL_DIR, exist_ok=True)

    print("Creating dataset...")

    X = []
    y = []
    label_map = {}

    label_id = 0

    for file in os.listdir(SEQ_DIR):
        label = file.split("_")[0]

        if label not in label_map:
            label_map[label] = label_id
            label_id += 1

        data = np.load(os.path.join(SEQ_DIR, file))

        for seq in data:
            X.append(seq)
            y.append(label_map[label])

    X = np.array(X)
    y = np.array(y)

    np.save(os.path.join(FINAL_DIR, "X.npy"), X)
    np.save(os.path.join(FINAL_DIR, "y.npy"), y)

    with open(os.path.join(FINAL_DIR, "label_map.json"), "w") as f:
        json.dump(label_map, f)

    print("Done!")
    print("X shape:", X.shape)