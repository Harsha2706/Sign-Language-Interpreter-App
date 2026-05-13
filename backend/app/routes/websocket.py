from fastapi import APIRouter, WebSocket
import numpy as np

from app.services.buffer import FrameBuffer
from app.services.inference import predict
from app.services.smoothing import PredictionSmoother
from app.config import SEQUENCE_LENGTH, SMOOTHING_WINDOW, CONFIDENCE_THRESHOLD

router = APIRouter()

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    buffer = FrameBuffer(SEQUENCE_LENGTH)
    smoother = PredictionSmoother(SMOOTHING_WINDOW)

    while True:
        data = await websocket.receive_json()

        keypoints = np.array(data["keypoints"])

        buffer.add(keypoints)

        if buffer.is_full():
            word, confidence = predict(buffer.get())

            # Apply threshold
            if confidence < CONFIDENCE_THRESHOLD:
                word = "Unknown"

            smoother.add(word)
            final_word = smoother.get()

            await websocket.send_json({
                "word": final_word,
                "confidence": confidence
            })