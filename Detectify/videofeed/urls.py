from django.urls import path
from . import views

urlpatterns = [
    path('live_feed/', views.live_feed_page, name='live_feed_page'),
    path('live_feed/stream/', views.live_feed_stream, name='live_feed_stream'),
    path('live_feed/label/', views.live_feed_label, name='live_feed_label'),
    path('process_image/', views.process_image, name='process_image'),
]