import os
from config import VIDEO_DIR, FRAME_DIR

def extract_frames():
    os.makedirs(FRAME_DIR, exist_ok=True)

    print("Starting frame extraction...")

    # Loop through each word folder
    for word in os.listdir(VIDEO_DIR):
        word_path = os.path.join(VIDEO_DIR, word)
        if not os.path.isdir(word_path):
            continue

        # Loop through all .mp4 files
        for video in os.listdir(word_path):
            if not video.endswith(".mp4"):
                continue

            video_path = os.path.join(word_path, video)
            name = f"{word}_{video.replace('.mp4','')}"
            out_path = os.path.join(FRAME_DIR, name)
            os.makedirs(out_path, exist_ok=True)

            # FFmpeg command
            os.system(f'ffmpeg -loglevel error -i "{video_path}" "{out_path}/frame_%04d.jpg"')

    print("Frame extraction completed!")

if __name__ == "__main__":
    extract_frames()