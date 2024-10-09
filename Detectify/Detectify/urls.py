from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
    path('surveillance/', include('surveillance.urls')),
    path('notifications/', include('notifications.urls')),
    path('frontend/', include('frontend.urls')),
]
