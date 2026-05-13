import torch
import sys
import os

# Add src folder to Python path
sys.path.append(r"F:\harsha\sign language\src")
from model import SignLanguageModel

# Define global model variable
model = None

# Define these according to your dataset
input_dim = 1662     # Example: number of features per frame (e.g., 42 keypoints × 3)
num_classes = 37    # Example: number of gesture classes

def load_model(path=r"F:\harsha\sign language\backend\model\model.pth"):
    """
    Loads the model from checkpoint.
    If checkpoint shapes don't match, only loads compatible layers.
    """
    global model
    model = SignLanguageModel(input_dim, num_classes)
    
    if os.path.exists(path):
        checkpoint = torch.load(path, map_location="cpu")
        model_dict = model.state_dict()
        
        # Only load matching layers
        pretrained_dict = {k: v for k, v in checkpoint.items() 
                           if k in model_dict and v.size() == model_dict[k].size()}
        model_dict.update(pretrained_dict)
        model.load_state_dict(model_dict)
        print(f"[INFO] Loaded {len(pretrained_dict)}/{len(model_dict)} layers from checkpoint")
    else:
        print(f"[WARNING] Checkpoint not found at {path}, model initialized randomly")
    
    model.eval()
    return model

def get_model():
    """
    Returns the loaded model.
    """
    return model