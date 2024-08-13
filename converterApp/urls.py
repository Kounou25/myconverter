from django.contrib import admin
from django.urls import path, include

from converterApp import views
from converterApp.views import get_progress

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('converter.urls')),
     path('progress/<str:file_id>/',get_progress, name='get_progress'),
]
