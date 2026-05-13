import torch
from app.models.model_loader import load_model, get_model

# Load the model manually
load_model()  # this sets the global model

model = get_model()
if model is None:
    raise ValueError("Model is not loaded. Something went wrong.")

# Create dummy input
batch_size = 2
seq_len = 64
input_dim = 1662  # must match your model_loader.py

dummy_input = torch.randn(batch_size, seq_len, input_dim)

# Run inference
with torch.no_grad():
    output = model(dummy_input)

print("Dummy input shape:", dummy_input.shape)
print("Model output shape:", output.shape)
print("Model output:", output)