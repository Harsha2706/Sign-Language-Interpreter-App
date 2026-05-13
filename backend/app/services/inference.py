import numpy as np
import torch
from ..models.model_loader import get_model

labels = ["Hello", "Thanks", "Yes", "No"]  # replace with your dataset

def predict(sequence):
    model = get_model()

    sequence = np.array(sequence)
    sequence = np.expand_dims(sequence, axis=0)

    sequence = torch.tensor(sequence, dtype=torch.float32)

    with torch.no_grad():
        output = model(sequence)
        probs = torch.softmax(output, dim=1).numpy()[0]

    idx = np.argmax(probs)
    return labels[idx], float(probs[idx])