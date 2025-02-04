from django.urls import path
from . import views

urlpatterns = [
    path('toggle/', views.toggle_processing_mode, name='toggle_processing_mode'),
]