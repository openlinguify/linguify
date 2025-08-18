from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import calendar_views, event_views, api_views, email_views

app_name = 'calendar'

# API Router for DRF ViewSets
router = DefaultRouter()
router.register(r'events', api_views.CalendarEventViewSet, basename='event')
router.register(r'event-types', api_views.CalendarEventTypeViewSet, basename='eventtype')
router.register(r'alarms', api_views.CalendarAlarmViewSet, basename='alarm')
router.register(r'attendees', api_views.CalendarAttendeeViewSet, basename='attendee')
router.register(r'recurrences', api_views.CalendarRecurrenceViewSet, basename='recurrence')
router.register(r'email-templates', email_views.CalendarEmailTemplateViewSet, basename='emailtemplate')
router.register(r'email-logs', email_views.CalendarEmailLogViewSet, basename='emaillog')

# Main URL patterns
urlpatterns = [
    # Calendar views
    path('', calendar_views.calendar_main, name='main'),
    path('agenda/', calendar_views.calendar_agenda, name='agenda'),
    path('settings/', calendar_views.calendar_settings, name='settings'),
    path('import-export/', calendar_views.import_export, name='import_export'),
    path('email-templates/', email_views.email_templates, name='email_templates'),
    
    # Calendar JSON API for FullCalendar
    path('json/', calendar_views.calendar_json, name='json'),
    
    # Event views
    path('event/create/', event_views.event_create, name='event_create'),
    path('event/<uuid:event_id>/', event_views.event_detail, name='event_detail'),
    path('event/<uuid:event_id>/edit/', event_views.event_edit, name='event_edit'),
    path('event/<uuid:event_id>/delete/', event_views.event_delete, name='event_delete'),
    path('event/<uuid:event_id>/respond/<str:response>/', event_views.event_respond, name='event_respond'),
    
    # Quick event creation (AJAX)
    path('quick-create/', event_views.quick_event_create, name='quick_create'),
    
    # Public invitation responses (no login required)
    path('invitation/<str:token>/<str:response>/', event_views.invitation_response, name='invitation_response'),
    
    # API endpoints
    path('api/', include(router.urls)),
]