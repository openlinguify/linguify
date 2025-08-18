from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Count
from datetime import datetime, timedelta, date
import calendar as python_calendar
import json

from ..models import CalendarEvent, CalendarEventType, CalendarAlarm, CalendarAttendee
from ..forms import CalendarEventForm, QuickEventForm


@login_required
def calendar_main(request):
    """
    Main calendar view with month/week/day views
    Based on Open Linguify's calendar interface
    """
    # Get view type from query params
    view_type = request.GET.get('view', 'month')
    date_str = request.GET.get('date')
    
    # Parse date or use current date
    if date_str:
        try:
            current_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            current_date = timezone.now().date()
    else:
        current_date = timezone.now().date()
    
    # Get events based on view type
    if view_type == 'month':
        events, date_range = get_month_events(request.user, current_date)
        template = 'calendar/calendar_month.html'
    elif view_type == 'week':
        events, date_range = get_week_events(request.user, current_date)
        template = 'calendar/calendar_week.html'
    elif view_type == 'day':
        events, date_range = get_day_events(request.user, current_date)
        template = 'calendar/calendar_day.html'
    else:
        # Default to month view
        events, date_range = get_month_events(request.user, current_date)
        template = 'calendar/calendar_month.html'
        view_type = 'month'
    
    # Get event types and alarms for quick create
    event_types = CalendarEventType.get_user_types(request.user)
    default_alarms = CalendarAlarm.get_default_alarms()
    
    context = {
        'events': events,
        'current_date': current_date,
        'date_range': date_range,
        'view_type': view_type,
        'event_types': event_types,
        'default_alarms': default_alarms,
        'calendar_colors': get_calendar_colors(),
        'today': timezone.now().date(),
    }
    
    return render(request, template, context)


@login_required
def calendar_agenda(request):
    """
    Agenda view showing upcoming events in list format
    """
    # Get date range
    start_date = timezone.now().date()
    end_date = start_date + timedelta(days=30)  # Next 30 days
    
    # Filter by date range if provided
    date_from = request.GET.get('from')
    date_to = request.GET.get('to')
    
    if date_from:
        try:
            start_date = datetime.strptime(date_from, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    if date_to:
        try:
            end_date = datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            pass
    
    # Get events
    events = CalendarEvent.objects.filter(
        Q(user_id=request.user) | Q(attendee_ids__partner_id=request.user),
        start__date__gte=start_date,
        start__date__lte=end_date,
        active=True
    ).distinct().select_related('user_id', 'event_type').prefetch_related('attendee_ids').order_by('start')
    
    # Group events by date
    events_by_date = {}
    for event in events:
        event_date = event.start.date()
        if event_date not in events_by_date:
            events_by_date[event_date] = []
        events_by_date[event_date].append(event)
    
    # Pagination
    paginator = Paginator(list(events_by_date.items()), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'events_by_date': dict(page_obj.object_list),
        'page_obj': page_obj,
        'start_date': start_date,
        'end_date': end_date,
        'today': timezone.now().date(),
    }
    
    return render(request, 'calendar/calendar_agenda.html', context)


@login_required
def calendar_json(request):
    """
    JSON API for FullCalendar integration
    Returns events in FullCalendar format
    """
    # Get date range from FullCalendar
    start_str = request.GET.get('start')
    end_str = request.GET.get('end')
    
    if not start_str or not end_str:
        return JsonResponse({'error': 'Missing start or end date'}, status=400)
    
    try:
        start_date = datetime.fromisoformat(start_str.replace('Z', '+00:00'))
        end_date = datetime.fromisoformat(end_str.replace('Z', '+00:00'))
    except ValueError:
        return JsonResponse({'error': 'Invalid date format'}, status=400)
    
    # Get events in date range
    events = CalendarEvent.objects.filter(
        Q(user_id=request.user) | Q(attendee_ids__partner_id=request.user),
        start__gte=start_date,
        start__lt=end_date,
        active=True
    ).distinct().select_related('user_id', 'event_type')
    
    # Convert to FullCalendar format
    calendar_events = []
    for event in events:
        calendar_event = {
            'id': str(event.id),
            'title': event.name,
            'start': event.start.isoformat(),
            'end': event.stop.isoformat(),
            'allDay': event.allday,
            'url': f'/calendar/event/{event.id}/',
            'backgroundColor': get_event_color(event),
            'borderColor': get_event_color(event),
            'textColor': get_text_color(event),
            'extendedProps': {
                'description': event.description,
                'location': event.location,
                'privacy': event.privacy,
                'organizer': event.user_id.get_full_name() or event.user_id.username,
                'attendees_count': event.get_attendees_count(),
                'type': event.event_type.name if event.event_type else None,
            }
        }
        calendar_events.append(calendar_event)
    
    return JsonResponse(calendar_events, safe=False)


@login_required
def import_export(request):
    """
    Import/Export calendar page
    """
    return render(request, 'calendar/import_export.html', {
        'page_title': 'Import/Export Calendar'
    })


def get_month_events(user, current_date):
    """Get events for month view"""
    # Get first and last day of month
    first_day = current_date.replace(day=1)
    
    # Get calendar month grid (including days from prev/next month)
    cal = python_calendar.monthcalendar(current_date.year, current_date.month)
    
    # Find actual start and end dates for the calendar grid
    start_date = first_day
    if cal[0][0] == 0:  # First week doesn't start on Monday
        # Find the actual first day shown
        for i, day in enumerate(cal[0]):
            if day != 0:
                start_date = first_day.replace(day=day)
                break
    
    # Find last date of month view
    last_week = cal[-1]
    if last_week[-1] == 0:  # Last week doesn't end on Sunday
        # Find actual last day shown
        for i in range(len(last_week) - 1, -1, -1):
            if last_week[i] != 0:
                end_date = first_day.replace(day=last_week[i])
                break
    else:
        end_date = first_day.replace(day=last_week[-1])
    
    # Add buffer to include events that span outside the visible range
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    
    # Get events
    events = CalendarEvent.objects.filter(
        Q(user_id=user) | Q(attendee_ids__partner_id=user),
        start__gte=start_datetime,
        start__lte=end_datetime,
        active=True
    ).distinct().select_related('user_id', 'event_type').order_by('start')
    
    return events, (start_date, end_date)


def get_week_events(user, current_date):
    """Get events for week view"""
    # Find start of week (Monday)
    start_of_week = current_date - timedelta(days=current_date.weekday())
    end_of_week = start_of_week + timedelta(days=6)
    
    start_datetime = datetime.combine(start_of_week, datetime.min.time())
    end_datetime = datetime.combine(end_of_week, datetime.max.time())
    
    events = CalendarEvent.objects.filter(
        Q(user_id=user) | Q(attendee_ids__partner_id=user),
        start__gte=start_datetime,
        start__lte=end_datetime,
        active=True
    ).distinct().select_related('user_id', 'event_type').order_by('start')
    
    return events, (start_of_week, end_of_week)


def get_day_events(user, current_date):
    """Get events for day view"""
    start_datetime = datetime.combine(current_date, datetime.min.time())
    end_datetime = datetime.combine(current_date, datetime.max.time())
    
    events = CalendarEvent.objects.filter(
        Q(user_id=user) | Q(attendee_ids__partner_id=user),
        start__gte=start_datetime,
        start__lte=end_datetime,
        active=True
    ).distinct().select_related('user_id', 'event_type').order_by('start')
    
    return events, (current_date, current_date)


def get_calendar_colors():
    """Get color palette for calendar"""
    return [
        {'name': 'Blue', 'value': '#007bff', 'index': 0},
        {'name': 'Green', 'value': '#28a745', 'index': 1},
        {'name': 'Red', 'value': '#dc3545', 'index': 2},
        {'name': 'Yellow', 'value': '#ffc107', 'index': 3},
        {'name': 'Purple', 'value': '#6f42c1', 'index': 4},
        {'name': 'Orange', 'value': '#fd7e14', 'index': 5},
        {'name': 'Pink', 'value': '#e83e8c', 'index': 6},
        {'name': 'Cyan', 'value': '#17a2b8', 'index': 7},
        {'name': 'Indigo', 'value': '#6610f2', 'index': 8},
        {'name': 'Teal', 'value': '#20c997', 'index': 9},
        {'name': 'Dark', 'value': '#343a40', 'index': 10},
        {'name': 'Secondary', 'value': '#6c757d', 'index': 11},
    ]


def get_event_color(event):
    """Get color for an event"""
    colors = get_calendar_colors()
    
    # Use event type color if available
    if event.event_type:
        color_index = event.event_type.color
    else:
        color_index = event.color
    
    # Ensure color index is valid
    if 0 <= color_index < len(colors):
        return colors[color_index]['value']
    
    return colors[0]['value']  # Default to blue


def get_text_color(event):
    """Get text color for an event (white or black based on background)"""
    # For now, return white for all colors
    # In a more sophisticated implementation, you'd calculate based on background brightness
    return '#ffffff'


@login_required
def calendar_settings(request):
    """
    Calendar settings and preferences
    """
    if request.method == 'POST':
        # Handle settings update
        default_view = request.POST.get('default_view', 'month')
        default_duration = request.POST.get('default_duration', 60)
        weekend_visible = request.POST.get('weekend_visible') == 'on'
        
        # Save to user profile/settings
        # This would typically be saved to a UserCalendarSettings model
        messages.success(request, 'Calendar settings updated successfully.')
        return redirect('calendar:settings')
    
    # Get current settings
    # This would typically come from a UserCalendarSettings model
    settings = {
        'default_view': 'month',
        'default_duration': 60,
        'weekend_visible': True,
        'default_alarms': CalendarAlarm.get_default_alarms(),
        'event_types': CalendarEventType.get_user_types(request.user),
    }
    
    context = {
        'settings': settings,
        'colors': get_calendar_colors(),
    }
    
    return render(request, 'calendar/calendar_settings.html', context)