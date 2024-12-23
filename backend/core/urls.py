# core/urls.py
from django.shortcuts import redirect
from django.contrib import admin
from django.urls import path, include

def redirect_to_admin(request):
    return redirect('admin/')

urlpatterns = [
    path('', redirect_to_admin),
    path('admin/', admin.site.urls),
    path('api/authentication/', include('authentication.urls')),
    path('api/v1/course/', include('course.urls', namespace='course')),
    path('api/v1/flashcard/', include('flashcard.urls', namespace='flashcard')),
]
