import cv2
import numpy as np
import tensorflow as tf
from django.conf import settings
import boto3
import json
from datetime import datetime, timedelta

# Load pre-trained model
model = tf.keras.applications.MobileNetV2(weights='imagenet')

# Cooldown period for detections
DETECTION_COOLDOWN = settings.DETECTION_COOLDOWN

# Dictionary to store the last detection time for each object
last_detection_time = {}

def capture_and_analyze_stream(rtsp_url):
    print("Analyzing stream from ", rtsp_url)
    capture = cv2.VideoCapture(rtsp_url)
    s3 = boto3.client('s3', 
                      aws_access_key_id=settings.AWS_ACCESS_KEY_ID, 
                      aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                      region_name=settings.AWS_REGION,
                      endpoint_url=settings.AWS_ENDPOINT_URL)
    print(f"Connected to S3 client with bucket name: {settings.AWS_STORAGE_BUCKET_NAME}")

    if not capture.isOpened():
        print("Error: Unable to open video stream")
        return None
    
    match_found = False
    detected_label = "Unknown"
    frame_counter = 0

    while True:
        ret, frame = capture.read()
        if not ret:
            break

        frame_counter += 1

        # Process every tenth frame
        if frame_counter % 10 == 0:
            frame_counter = 0
            # Preprocess frame for model
            img = cv2.resize(frame, (224, 224))
            img = np.expand_dims(img, axis=0)
            img = tf.keras.applications.mobilenet_v2.preprocess_input(img)

            # Predict
            preds = model.predict(img)
            decoded_preds = tf.keras.applications.mobilenet_v2.decode_predictions(preds, top=1)[0]
            detected_label = "Unknown"
            match_found = False
            # Check if recognized object is in the defined list
            recognized_objects = ['tabby', 'cat', 'dog', 'person', 'gun', 'knife', 'can', 'bottle']
            for _, label, _ in decoded_preds:
                if label in recognized_objects:
                    current_time = datetime.now()
                    if label not in last_detection_time or current_time - last_detection_time[label] > timedelta(seconds=DETECTION_COOLDOWN):
                        print("Recognized object:", label)
                        match_found = True
                        detected_label = label
                        last_detection_time[label] = current_time
                        # Save snapshot and metadata
                        _, buffer = cv2.imencode('.jpg', frame)
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f'{label}_{timestamp}.jpg', Body=buffer.tobytes())
                        metadata = {'object': label, 'confidence': float(preds[0][0]), 'timestamp': timestamp}
                        s3.put_object(Bucket=settings.AWS_STORAGE_BUCKET_NAME, Key=f'{label}_{timestamp}_meta.json', Body=json.dumps(metadata))

                        # Send notification
                        send_notification(label, metadata)
                        break

        # Encode frame as JPEG
        _, jpeg = cv2.imencode('.jpg', frame)
        frame_bytes = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n\r\n', match_found, detected_label)

    capture.release()

def send_notification(label, metadata):
    print(f'Object detected: {label}\nMetadata: {metadata}')
    return
    import requests
    bot_token = 'YOUR_TELEGRAM_BOT_TOKEN'
    chat_id = 'YOUR_CHAT_ID'
    message = f'Object detected: {label}\nMetadata: {metadata}'
    url = f'https://api.telegram.org/bot{bot_token}/sendMessage'
    requests.post(url, data={'chat_id': chat_id, 'text': message})