"""
Sign Language Recognition — FastAPI Backend
-------------------------------------------
Feature layout (258 per frame, NO face landmarks):
  - Pose:       33 × 4 = 132  (x, y, z, visibility)
  - Left hand:  21 × 3 = 63   (x, y, z)
  - Right hand: 21 × 3 = 63   (x, y, z)
  Total:                 258

Model expects: (1, SEQUENCE_LENGTH, 258)
"""

import json
import importlib.util
import sys
from collections import deque
from pathlib import Path

import numpy as np
import torch
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

# ─────────────────────────────────────────────
#  Constants
# ─────────────────────────────────────────────
SEQUENCE_LENGTH     = 30
CONFIDENCE_THRESHOLD = 0.4
FEATURE_SIZE        = 258        # Pose(132) + LH(63) + RH(63)
MODEL_PTH           = Path(__file__).parent.parent / "model" / "model.pth"
MODEL_PY            = Path(__file__).parent / "model.py"

LABELS = [
    "angry", "bad", "bathroom", "come", "day", "drink", "eat",
    "family", "fine", "friend", "go", "good", "happy", "hello",
    "help", "how", "love", "more", "name", "night", "no",
    "please", "sad", "school", "sorry", "stop", "thank you", "time",
    "understand", "wait", "want", "what", "where", "who", "why",
    "work", "yes",
]

# ─────────────────────────────────────────────
#  Model Loading
# ─────────────────────────────────────────────
def _load_model() -> torch.nn.Module:
    """Dynamically load SignLanguageModel from src/model.py and restore weights."""
    if not MODEL_PY.exists():
        raise FileNotFoundError(f"model.py not found at {MODEL_PY}")
    if not MODEL_PTH.exists():
        raise FileNotFoundError(f"model.pth not found at {MODEL_PTH}")

    spec = importlib.util.spec_from_file_location("sign_model_def", str(MODEL_PY))
    module = importlib.util.module_from_spec(spec)   # type: ignore[arg-type]
    sys.modules["sign_model_def"] = module
    spec.loader.exec_module(module)                   # type: ignore[union-attr]

    SignLanguageModel = module.SignLanguageModel

    # NOTE: input_dim=258 to match training (NO face landmarks)
    mdl = SignLanguageModel(input_dim=FEATURE_SIZE, num_classes=len(LABELS))
    
    # Safely load weights, skipping dimension mismatches (useful if user is migrating from 1662 to 258)
    checkpoint = torch.load(MODEL_PTH, map_location="cpu")
    model_dict = mdl.state_dict()
    pretrained_dict = {
        k: v for k, v in checkpoint.items()
        if k in model_dict and v.size() == model_dict[k].size()
    }
    model_dict.update(pretrained_dict)
    mdl.load_state_dict(model_dict)
    
    mdl.eval()
    print(f"[OK] Model loaded  |  input_dim={FEATURE_SIZE}  |  classes={len(LABELS)}  |  layers loaded={len(pretrained_dict)}/{len(model_dict)}")
    return mdl


model = _load_model()

# ─────────────────────────────────────────────
#  FastAPI App
# ─────────────────────────────────────────────
app = FastAPI(title="Sign Language Recognition API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─────────────────────────────────────────────
#  Keypoint Extraction  (STRICTLY 258 features)
# ─────────────────────────────────────────────
def extract_keypoints(results) -> np.ndarray:
    """
    Extract pose + hand landmarks only.
    Face landmarks are intentionally excluded.

    Returns
    -------
    np.ndarray of shape (258,)
        [pose(132) | left_hand(63) | right_hand(63)]
    """
    # --- Pose: 33 landmarks × 4 = 132 ---
    if results.pose_landmarks:
        pose = np.array(
            [[lm.x, lm.y, lm.z, lm.visibility]
             for lm in results.pose_landmarks.landmark],
            dtype=np.float32,
        ).flatten()
    else:
        pose = np.zeros(33 * 4, dtype=np.float32)

    # --- Left hand: 21 landmarks × 3 = 63 ---
    if results.left_hand_landmarks:
        lh = np.array(
            [[lm.x, lm.y, lm.z]
             for lm in results.left_hand_landmarks.landmark],
            dtype=np.float32,
        ).flatten()
    else:
        lh = np.zeros(21 * 3, dtype=np.float32)

    # --- Right hand: 21 landmarks × 3 = 63 ---
    if results.right_hand_landmarks:
        rh = np.array(
            [[lm.x, lm.y, lm.z]
             for lm in results.right_hand_landmarks.landmark],
            dtype=np.float32,
        ).flatten()
    else:
        rh = np.zeros(21 * 3, dtype=np.float32)

    keypoints = np.concatenate([pose, lh, rh])   # (258,)

    # --- Shape guard ---
    assert keypoints.shape == (FEATURE_SIZE,), (
        f"[extract_keypoints] Expected ({FEATURE_SIZE},), got {keypoints.shape}"
    )
    return keypoints


# ─────────────────────────────────────────────
#  Prediction
# ─────────────────────────────────────────────
def predict(sequence: list) -> dict:
    """
    Run inference on a buffered sequence of frames.

    Parameters
    ----------
    sequence : list of lists  shape (SEQUENCE_LENGTH, 258)

    Returns
    -------
    dict  { label: str, confidence: float }
    """
    x = np.array(sequence, dtype=np.float32)          # (30, 258)
    print(f"[predict] Input shape  : {x.shape}")       # debug

    if x.shape != (SEQUENCE_LENGTH, FEATURE_SIZE):
        raise ValueError(
            f"[predict] Bad input shape {x.shape}. "
            f"Expected ({SEQUENCE_LENGTH}, {FEATURE_SIZE})"
        )

    tensor = torch.tensor(x).unsqueeze(0)              # (1, 30, 258)
    print(f"[predict] Tensor shape : {tensor.shape}")  # debug

    with torch.no_grad():
        logits = model(tensor)                         # (1, num_classes)
        probs  = torch.softmax(logits, dim=1)          # explicit softmax
        conf, idx = torch.max(probs, dim=1)
        confidence = float(conf.item())
        label      = LABELS[int(idx.item())]

    print(f"[predict] → {label!r}  confidence={confidence:.3f}")
    return {"label": label, "confidence": round(confidence, 4)}


# ─────────────────────────────────────────────
#  WebSocket — raw keypoints path
#  Frontend sends one frame's keypoints per message (list of 258 floats).
#  Backend buffers them; fires prediction every SEQUENCE_LENGTH frames.
# ─────────────────────────────────────────────
@app.websocket("/ws/keypoints")
async def ws_keypoints(websocket: WebSocket):
    """
    Receive pre-extracted keypoints (258 floats) per frame,
    buffer into sequences, predict when full.
    """
    await websocket.accept()
    print("[OK] [ws/keypoints] Client connected")

    buffer: deque = deque(maxlen=SEQUENCE_LENGTH)

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                frame_kp = json.loads(raw)            # expect list[float] len=258
            except json.JSONDecodeError as e:
                await websocket.send_text(json.dumps({"error": f"JSON parse error: {e}"}))
                continue

            if not isinstance(frame_kp, list) or len(frame_kp) != FEATURE_SIZE:
                msg = f"Expected list of {FEATURE_SIZE} floats, got {type(frame_kp).__name__}[{len(frame_kp) if isinstance(frame_kp, list) else '?'}]"
                print(f"⚠️  {msg}")
                await websocket.send_text(json.dumps({"error": msg}))
                continue

            buffer.append(frame_kp)
            print(f"[ws/keypoints] Buffer: {len(buffer)}/{SEQUENCE_LENGTH}")

            if len(buffer) == SEQUENCE_LENGTH:
                try:
                    result = predict(list(buffer))
                    if result["confidence"] >= CONFIDENCE_THRESHOLD:
                        await websocket.send_text(json.dumps(result))
                    else:
                        await websocket.send_text(json.dumps({
                            "label": "uncertain",
                            "confidence": result["confidence"],
                        }))
                except Exception as e:
                    print(f"❌ Prediction error: {e}")
                    await websocket.send_text(json.dumps({"error": str(e)}))

    except WebSocketDisconnect:
        print("INFO:  [ws/keypoints] Client disconnected")
    except Exception as e:
        print(f"[ERROR] [ws/keypoints] Unhandled error: {e}")


# ─────────────────────────────────────────────
#  WebSocket — full sequence path
#  Frontend sends a complete 30-frame sequence (list[list[258]]) per message.
# ─────────────────────────────────────────────
@app.websocket("/ws")
async def ws_sequence(websocket: WebSocket):
    """
    Receive a complete sequence of SEQUENCE_LENGTH frames per message.
    Each message is JSON: list[list[float]]  shape (30, 258).
    """
    await websocket.accept()
    print("[OK] [ws] Client connected")

    try:
        while True:
            raw = await websocket.receive_text()

            try:
                sequence = json.loads(raw)
            except json.JSONDecodeError as e:
                await websocket.send_text(json.dumps({"error": f"JSON parse error: {e}"}))
                continue

            if not isinstance(sequence, list):
                await websocket.send_text(json.dumps({"error": "Expected a JSON array"}))
                continue

            if len(sequence) != SEQUENCE_LENGTH:
                msg = f"Expected {SEQUENCE_LENGTH} frames, got {len(sequence)}"
                print(f"⚠️  {msg}")
                await websocket.send_text(json.dumps({"error": msg}))
                continue

            # Validate inner dimension
            for i, frame in enumerate(sequence):
                if not isinstance(frame, list) or len(frame) != FEATURE_SIZE:
                    msg = f"Frame {i}: expected list[{FEATURE_SIZE}], got {type(frame).__name__}[{len(frame) if isinstance(frame, list) else '?'}]"
                    await websocket.send_text(json.dumps({"error": msg}))
                    break
            else:
                try:
                    result = predict(sequence)
                    await websocket.send_text(json.dumps(result))
                except Exception as e:
                    print(f"❌ Prediction error: {e}")
                    await websocket.send_text(json.dumps({"error": str(e)}))

    except WebSocketDisconnect:
        print("INFO:  [ws] Client disconnected")
    except Exception as e:
        print(f"[ERROR] [ws] Unhandled error: {e}")


# ─────────────────────────────────────────────
#  Health check
# ─────────────────────────────────────────────
@app.get("/health")
def health():
    return {
        "status": "ok",
        "feature_size": FEATURE_SIZE,
        "sequence_length": SEQUENCE_LENGTH,
        "classes": len(LABELS),
        "model": str(MODEL_PTH.name),
    }