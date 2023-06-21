from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('study_project.urls')),
    path('api/', include('study_project.api.urls')),
]
