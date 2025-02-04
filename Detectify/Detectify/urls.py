from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('videofeed/', include('videofeed.urls')),
    path('notifications/', include('notification.urls')),
    path('frontend/', include('frontend.urls')),
]
