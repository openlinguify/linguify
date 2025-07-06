"""
URL configuration for LMS project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('tenants/', include('lms.apps.tenants.urls')),
    path('org/<str:org_slug>/', include([
        path('', include('lms.apps.core.urls', namespace='org-core')),
        path('courses/', include('lms.apps.courses.urls', namespace='org-courses')),
        path('students/', include('lms.apps.students.urls', namespace='org-students')),
        path('instructors/', include('lms.apps.instructors.urls', namespace='org-instructors')),
        path('assessments/', include('lms.apps.assessments.urls', namespace='org-assessments')),
        path('analytics/', include('lms.apps.analytics.urls', namespace='org-analytics')),
        path('content/', include('lms.apps.content.urls', namespace='org-content')),
        path('administration/', include('lms.apps.administration.urls', namespace='org-administration')),
    ])),
    path('institutions/', include('lms.apps.institutions.urls')),
    path('api/', include('lms.apps.api.urls')),
    path('', include('lms.apps.core.urls')),  # Must be last
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)