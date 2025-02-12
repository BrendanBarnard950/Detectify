import cv2
import numpy as np
import tensorflow as tf
import threading
import time
from datetime import datetime, timedelta
from django.conf import settings
import boto3

class StreamDetector:
    def __init__(self, stream_url):
        self.stream_url = stream_url
        self.stream = None
        self.newest_frame = None
        self.newest_guess = "Unknown"
        self.thread_lock = threading.Lock()
        self.running = True
        self.frame_counter = 0
        
        # For now these are the only two confirmed detections I know work with the model. Ideally I'd train my own with broader classifications like 'cat'
        # and 'dude', but for now this is more POC than anything.
        self.recognized_objects = ['tabby', 'tiger_cat']
        self.cooldown = settings.DETECTION_COOLDOWN
        
        # Loading the model once because the console has a fit every time it gets loaded because my hardware is very sad, and this prevents it from having a fit with
        # every frame. It's also probably just a good idea, since we dont have to worry about overusing resources by constantly loading and killing the model
        self.model = tf.keras.applications.MobileNetV2(weights='imagenet')
        
        # Setup S3. Don't commit keys. Brendan, don't commit your keys. Make sure settings_local is in the gitignore. Brendan, look at me. Do. Not. Commit. The. Keys.
        self.s3 = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION,
            endpoint_url=settings.AWS_ENDPOINT_URL
        )
        self.bucket = settings.AWS_STORAGE_BUCKET_NAME
        
        self.latest_detection = {}
        
        # This threading is bound to cause issues but the FE label, indicator, and actual stream all need it. It doesn't stop safely, and until I figure out how to capture
        # a keyboard interrupt and forcibly close the thread it's going to stay cursed. It SHOULD kill the thread when the server is stopped, but it might not, so...
        # ToDo: Find a way to kill the thread reliably when the server dies
        self.thread = threading.Thread(target=self._capture_loop, daemon=True)
        self.thread.start()

    def _capture_loop(self):
        """
        Tries to open the stream (in a thread, for the time being), grabs frames, makes them jpegs, and gives them to the detection loop
        """
        print("Analyzing stream from ", self.stream_url)
        self.stream = cv2.VideoCapture(self.stream_url)
        if not self.stream.isOpened():
            print("Error: Unable to open video stream")
            return
        
        while self.running:
            # This loop has no way to actually die.
            # ToDo: Add button that kills the stream, and also add retry limit to trying to read frames from the stream
            ret, frame = self.stream.read()
            if not ret:
                print("Error: Failed to read frame")
                time.sleep(1) 
                continue

            self.frame_counter += 1

            # Run detection every 300 frames, because anything more will cause my poor graphics card to explode. My stream goes at 10fps, so this amounts to a detection
            # every 30 seconds. This is a good balance between detection frequency and not setting my desk on fire.
            if self.frame_counter % 300 == 0:
                self.frame_counter = 0
                self._run_detection(frame)

            # Encode the current frame as JPEG. There is likely a better way to handle this stream.
            # ToDo: Look into live-scanning of the video, instead of frame by frame
            success, jpeg = cv2.imencode('.jpg', frame)
            if success:
                with self.thread_lock:
                    self.newest_frame = jpeg.tobytes()

        # Cleanup. This can't be reached since the while loop can't be escaped, but it will be reached once I add that button to kill te stream
        self.stream.release()

    def _run_detection(self, frame):
        """
        Checks passed frame against the class list of valid objects for detection, and if it finds a match, uploads the frame to S3.
        """
        img = tf.keras.applications.mobilenet_v2.preprocess_input(
            np.expand_dims(
                cv2.resize(
                    frame, (224, 224)
                    ), 
                axis=0
            )
        )

        predictions = self.model.predict(img)
        # I should cache old results so that I can display new recognitions that are within the cooldown window and are different from the "main"
        # recognition, as long as they are above the confidence threshold (arbitrarliy chose 0.85, but had to lower it to 0.4 because low stream resolution killed confidence)
        # ToDo: That ^^^
        decoded_predictions = tf.keras.applications.mobilenet_v2.decode_predictions(predictions, top=1)[0]
        
        for _, guess, confidence in decoded_predictions:
            print(f"Detected {guess} with confidence {confidence}")
            if guess in self.recognized_objects and confidence > 0.4:
                self.newest_guess = guess
                current_time = datetime.now()
                
                # We dont want to upload the same item to S3 over and over within the cooldown window
                if (guess not in self.latest_detection or (current_time - self.latest_detection[guess]) > timedelta(seconds=self.cooldown)):
                    self.latest_detection[guess] = current_time
                    
                    # This is commented out cause I am scared of Bezos taking all of my money. It works.

                    # _, buffer = cv2.imencode('.jpg', frame)
                    # timestamp = current_time.strftime("%Y%m%d_%H%M%S")
                    
                    # self.s3.put_object(
                    #     Bucket=self.bucket,
                    #     Key=f'{guess}_{timestamp}.jpg',
                    #     Body=buffer.tobytes()
                    # )
                    
                    
                    # metadata = {'object': guess, 'confidence': confidence, 'timestamp': timestamp}
                    # self.s3.put_object(
                    #     Bucket=self.bucket,
                    #     Key=f'{guess}_{timestamp}_meta.json',
                    #     Body=json.dumps(metadata)
                    # )
                    break
            else:
                self.newest_guess = "Unknown"

    def get_jpeg_frame(self):
        """
        Return the newest frame as a JPEG.
        """
        with self.thread_lock:
            return self.newest_frame

    def get_label(self):
        """
        Return the most recent guess.
        """
        return self.newest_guess

stream_detector = StreamDetector(settings.STREAM_URL)
