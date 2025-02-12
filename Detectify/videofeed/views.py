"""
First time I've really had to content with the concept of yielding. I've never really done something like this, and I'm not sure if this is the best approach for this videostream approach.
ToDo: Research possible alternatives.
"""
from django.http import StreamingHttpResponse
from django.shortcuts import render
from .utils.stream_handler import stream_detector
import time

def live_feed_page(request):
    """
    Acts as a base view for the page that houses the stream and label. 
    """
    return render(request, 'videofeed/live_feed.html')

def live_feed_stream(request):
    """
    This view gets the frames from the stream for the FE
    """
    def frame_fetcher():
        """
        Constantly fetches the frames from the RTSP stream as jpgs. I think this is bad, but it's the first way that I found on Google for image recognition from an RTSP stream and this was more
        to mess with image recognition than to make an efficient streaming platform.
        """
        while True:
            frame = stream_detector.get_jpeg_frame()
            if frame:
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
            else:
                # This is just to buffer things if the stream hasn't started yet.
                time.sleep(0.1)

    return StreamingHttpResponse(frame_fetcher(), content_type='multipart/x-mixed-replace; boundary=frame')

def live_feed_label(request):
    """
    This sends through the detected label to the FE
    """
    def label_fetcher():
        """
        Grabs the image guess that was most recently detected.
        """
        detected_label = stream_detector.get_label()
        yield f"data: {detected_label}\n\n"
    return StreamingHttpResponse(label_fetcher(), content_type='text/event-stream')
