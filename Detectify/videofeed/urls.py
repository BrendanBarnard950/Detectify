from django.urls import path
from . import views

urlpatterns = [
    path('', views.live_feed_page, name='live_feed_page'),
    path('stream/', views.live_feed_stream, name='live_feed_stream'),
    path('label/', views.live_feed_label, name='live_feed_label'),
]