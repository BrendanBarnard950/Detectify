from django.urls import path
from . import views

urlpatterns = [
    path('live_feed/', views.live_feed, name='live_feed'),
    path('process/', views.process_image, name='process_image'),
]