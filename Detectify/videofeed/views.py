from django.shortcuts import render
from django.http import StreamingHttpResponse, HttpResponse
from .utils.stream_handler import capture_and_analyze_stream
from Detectify.settings import STREAM_URL

def live_feed_page(request):
    return render(request, 'videofeed/live_feed.html')

def live_feed_stream(request):
    def stream_generator():
        for frame, _, _ in capture_and_analyze_stream(STREAM_URL):
            yield frame

    return StreamingHttpResponse(stream_generator(), content_type='multipart/x-mixed-replace; boundary=frame')

def live_feed_label(request):
    def label_generator():
        for _, _, detected_label in capture_and_analyze_stream(STREAM_URL):
            yield f'data: {detected_label}\n\n'

    return HttpResponse(label_generator(), content_type='text/event-stream')

def process_image(request):
    # Placeholder for processing logic
    return render(request, 'videofeed/result.html', {'result': 'Processing result'})