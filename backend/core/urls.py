# backend/core/urls.py
from django.shortcuts import redirect
from django.contrib import admin
from django.urls import path, include

def redirect_to_admin(request):
    return redirect('admin/')

urlpatterns = [
    path('', redirect_to_admin),
    path('admin/', admin.site.urls),
    path('api/v1/auth/', include('authentication.urls')),
    path('api/v1/course/', include('course.urls', namespace='course')),
    path('api/v1/revision/', include('revision.urls', namespace='revision')),
    path('api/v1/flashcard/', include('flashcard.urls', namespace='flashcard')),
    path('api/v1/notebook/', include('notebook.urls', namespace='notebook')),
    path('api/chat/', include('chat.urls', namespace='chat')),
    path('api/v1/task/', include('task.urls', namespace='task')),
]
