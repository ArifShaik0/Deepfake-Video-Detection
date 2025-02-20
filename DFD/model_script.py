import cv2
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array
from tensorflow.keras.applications.inception_v3 import preprocess_input

def classify_video(video_path, model):
    frames = extract_frames(video_path)
    predictions = []

    for frame in frames:
        processed_frame = preprocess_frame(frame)
        prediction = model.predict(processed_frame)
        predictions.append(prediction)

    mean_prediction = np.mean(predictions)
    return "Real" if mean_prediction > 0.5 else "Fake"

def extract_frames(video_path, frames_per_second=2):
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)
    interval = int(fps / frames_per_second)

    frames = []
    count = 0
    while True:
        ret, frame = video.read()
        if not ret:
            break

        if count % interval == 0:
            frames.append(frame)

        count += 1

    video.release()
    return frames

def preprocess_frame(frame, target_size=(224, 224)):  # Adjust target_size to match your model input
    frame = cv2.resize(frame, target_size)
    frame = img_to_array(frame)
    frame = np.expand_dims(frame, axis=0)
    frame = preprocess_input(frame)
    return frame
