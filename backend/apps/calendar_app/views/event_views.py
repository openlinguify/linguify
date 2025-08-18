from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from datetime import datetime, timedelta
import json

from ..models import (
    CalendarEvent, CalendarEventType, CalendarAlarm, 
    CalendarAttendee, CalendarRecurrence, CalendarInvitation
)
from ..forms import CalendarEventForm, QuickEventForm, RecurrenceForm


@login_required
def event_detail(request, event_id):
    """
    Display event details
    """
    event = get_object_or_404(CalendarEvent, id=event_id)
    
    # Check if user can view this event
    if not event.can_view(request.user):
        return HttpResponseForbidden("You don't have permission to view this event.")
    
    # Get attendees
    attendees = event.attendee_ids.select_related('partner_id').order_by('common_name')
    
    # Get user's attendance status if they are an attendee
    user_attendance = None
    if event.is_attendee(request.user):
        user_attendance = attendees.filter(partner_id=request.user).first()
    
    context = {
        'event': event,
        'attendees': attendees,
        'user_attendance': user_attendance,
        'can_edit': event.can_edit(request.user),
        'is_organizer': event.is_organizer(request.user),
        'recurrence_info': event.get_recurrence_display(),
    }
    
    return render(request, 'calendar/event_detail.html', context)


@login_required
def event_create(request):
    """
    Create a new calendar event
    """
    if request.method == 'POST':
        form = CalendarEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user_id = request.user
            event.save()
            
            # Save many-to-many relationships
            form.save_m2m()
            
            # Create organizer as attendee
            CalendarAttendee.get_or_create_for_organizer(event)
            
            # Handle attendees
            attendees_data = request.POST.get('attendees_json')
            if attendees_data:
                try:
                    attendees = json.loads(attendees_data)
                    for attendee_data in attendees:
                        if attendee_data.get('email'):
                            CalendarAttendee.create_for_email(
                                event=event,
                                email=attendee_data['email'],
                                name=attendee_data.get('name')
                            )
                except json.JSONDecodeError:
                    pass
            
            # Handle recurrence
            if form.cleaned_data.get('is_recurring'):
                recurrence_form = RecurrenceForm(request.POST)
                if recurrence_form.is_valid():
                    recurrence = CalendarRecurrence.create_from_event(
                        event, **recurrence_form.cleaned_data
                    )
                    # Generate recurring events
                    recurrence.apply_recurrence(limit=50)
            
            # Send invitations
            if request.POST.get('send_invitations'):
                send_event_invitations(event)
            
            messages.success(request, f'Event "{event.name}" created successfully.')
            return redirect('calendar:event_detail', event_id=event.id)
    else:
        # Pre-fill with date/time if provided
        initial_data = {}
        start_date = request.GET.get('date')
        start_time = request.GET.get('time')
        
        if start_date:
            try:
                initial_data['start'] = datetime.strptime(start_date, '%Y-%m-%d')
                if start_time:
                    time_obj = datetime.strptime(start_time, '%H:%M').time()
                    initial_data['start'] = datetime.combine(
                        initial_data['start'].date(), time_obj
                    )
                
                # Default to 1 hour duration
                initial_data['stop'] = initial_data['start'] + timedelta(hours=1)
            except ValueError:
                pass
        
        form = CalendarEventForm(initial=initial_data)
    
    # Get available options
    event_types = CalendarEventType.get_user_types(request.user)
    default_alarms = CalendarAlarm.get_default_alarms()
    
    context = {
        'form': form,
        'event_types': event_types,
        'default_alarms': default_alarms,
        'is_create': True,
    }
    
    return render(request, 'calendar/event_form.html', context)


@login_required
def event_edit(request, event_id):
    """
    Edit an existing calendar event
    """
    event = get_object_or_404(CalendarEvent, id=event_id)
    
    # Check permissions
    if not event.can_edit(request.user):
        return HttpResponseForbidden("You don't have permission to edit this event.")
    
    if request.method == 'POST':
        form = CalendarEventForm(request.POST, instance=event)
        if form.is_valid():
            event = form.save()
            
            # Handle attendees update
            attendees_data = request.POST.get('attendees_json')
            if attendees_data:
                try:
                    attendees = json.loads(attendees_data)
                    # Clear existing attendees (except organizer)
                    event.attendee_ids.exclude(partner_id=event.user_id).delete()
                    
                    # Add new attendees
                    for attendee_data in attendees:
                        if attendee_data.get('email'):
                            CalendarAttendee.create_for_email(
                                event=event,
                                email=attendee_data['email'],
                                name=attendee_data.get('name')
                            )
                except json.JSONDecodeError:
                    pass
            
            # Send update notifications
            if request.POST.get('send_updates'):
                send_event_updates(event)
            
            messages.success(request, f'Event "{event.name}" updated successfully.')
            return redirect('calendar:event_detail', event_id=event.id)
    else:
        form = CalendarEventForm(instance=event)
    
    # Get current attendees for pre-population
    attendees = list(event.attendee_ids.exclude(partner_id=event.user_id).values(
        'email', 'common_name'
    ))
    
    # Get available options
    event_types = CalendarEventType.get_user_types(request.user)
    default_alarms = CalendarAlarm.get_default_alarms()
    
    context = {
        'form': form,
        'event': event,
        'attendees_json': json.dumps(attendees),
        'event_types': event_types,
        'default_alarms': default_alarms,
        'is_edit': True,
    }
    
    return render(request, 'calendar/event_form.html', context)


@login_required
def event_delete(request, event_id):
    """
    Delete a calendar event
    """
    event = get_object_or_404(CalendarEvent, id=event_id)
    
    # Check permissions
    if not event.can_edit(request.user):
        return HttpResponseForbidden("You don't have permission to delete this event.")
    
    if request.method == 'POST':
        event_name = event.name
        
        # Handle recurring event deletion
        delete_type = request.POST.get('delete_type', 'single')
        
        if event.recurrency and event.recurrence_id:
            if delete_type == 'all':
                # Delete all occurrences
                CalendarEvent.objects.filter(recurrence_id=event.recurrence_id).delete()
                event.recurrence_id.delete()
                messages.success(request, f'All occurrences of "{event_name}" deleted.')
            elif delete_type == 'future':
                # Delete this and future occurrences
                CalendarEvent.objects.filter(
                    recurrence_id=event.recurrence_id,
                    start__gte=event.start
                ).delete()
                # Update recurrence to end before this date
                event.recurrence_id.stop_at(event.start - timedelta(days=1))
                messages.success(request, f'This and future occurrences of "{event_name}" deleted.')
            else:
                # Delete only this occurrence
                event.delete()
                messages.success(request, f'Event "{event_name}" deleted.')
        else:
            # Regular event deletion
            event.delete()
            messages.success(request, f'Event "{event_name}" deleted.')
        
        return redirect('calendar:main')
    
    context = {
        'event': event,
        'is_recurring': event.recurrency and event.recurrence_id,
    }
    
    return render(request, 'calendar/event_delete.html', context)


@login_required
def quick_event_create(request):
    """
    Create a quick event via AJAX
    """
    if request.method == 'POST':
        form = QuickEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user_id = request.user
            event.save()
            
            # Create organizer as attendee
            CalendarAttendee.get_or_create_for_organizer(event)
            
            return JsonResponse({
                'success': True,
                'event': {
                    'id': str(event.id),
                    'title': event.name,
                    'start': event.start.isoformat(),
                    'end': event.stop.isoformat(),
                    'url': f'/calendar/event/{event.id}/'
                }
            })
        else:
            return JsonResponse({
                'success': False,
                'errors': form.errors
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})


@login_required
def event_respond(request, event_id, response):
    """
    Respond to an event invitation
    """
    event = get_object_or_404(CalendarEvent, id=event_id)
    
    # Check if user is an attendee
    try:
        attendee = event.attendee_ids.get(partner_id=request.user)
    except CalendarAttendee.DoesNotExist:
        return HttpResponseForbidden("You are not invited to this event.")
    
    # Update response
    if response == 'accept':
        attendee.do_accept()
        messages.success(request, f'You have accepted the invitation to "{event.name}".')
    elif response == 'decline':
        attendee.do_decline()
        messages.success(request, f'You have declined the invitation to "{event.name}".')
    elif response == 'tentative':
        attendee.do_tentative()
        messages.success(request, f'You have marked "{event.name}" as tentative.')
    else:
        messages.error(request, 'Invalid response.')
    
    # If AJAX request, return JSON
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'status': attendee.state,
            'status_display': attendee.get_state_display()
        })
    
    return redirect('calendar:event_detail', event_id=event.id)


def invitation_response(request, token, response):
    """
    Respond to event invitation via email token (public view)
    """
    try:
        attendee = get_object_or_404(CalendarAttendee, access_token=token)
        event = attendee.event_id
        
        # Update response
        if response == 'accept':
            attendee.do_accept()
            message = f'You have accepted the invitation to "{event.name}".'
        elif response == 'decline':
            attendee.do_decline()
            message = f'You have declined the invitation to "{event.name}".'
        elif response == 'tentative':
            attendee.do_tentative()
            message = f'You have marked "{event.name}" as tentative.'
        else:
            message = 'Invalid response.'
        
        context = {
            'event': event,
            'attendee': attendee,
            'message': message,
            'response': response,
        }
        
        return render(request, 'calendar/invitation_response.html', context)
        
    except CalendarAttendee.DoesNotExist:
        return render(request, 'calendar/invitation_invalid.html')


def send_event_invitations(event):
    """
    Send email invitations for an event
    """
    attendees = event.attendee_ids.exclude(partner_id=event.user_id)
    
    for attendee in attendees:
        # Create invitation record
        invitation = CalendarInvitation.objects.create(
            attendee=attendee,
            event=event,
            subject=f'Invitation: {event.name}',
            message=f'You are invited to "{event.name}" on {event.start.strftime("%B %d, %Y at %I:%M %p")}'
        )
        
        # Send email
        try:
            context = {
                'event': event,
                'attendee': attendee,
                'invitation': invitation,
                'accept_url': f'{settings.SITE_URL}/calendar/invitation/{attendee.access_token}/accept/',
                'decline_url': f'{settings.SITE_URL}/calendar/invitation/{attendee.access_token}/decline/',
                'tentative_url': f'{settings.SITE_URL}/calendar/invitation/{attendee.access_token}/tentative/',
            }
            
            html_content = render_to_string('calendar/email/invitation.html', context)
            text_content = render_to_string('calendar/email/invitation.txt', context)
            
            send_mail(
                subject=invitation.subject,
                message=text_content,
                html_message=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[attendee.email],
                fail_silently=False,
            )
            
            invitation.mark_sent()
            
        except Exception as e:
            invitation.mark_failed(str(e))


def send_event_updates(event):
    """
    Send update notifications for an event
    """
    attendees = event.attendee_ids.exclude(partner_id=event.user_id)
    
    for attendee in attendees:
        try:
            context = {
                'event': event,
                'attendee': attendee,
                'update_message': f'The event "{event.name}" has been updated.',
            }
            
            html_content = render_to_string('calendar/email/event_update.html', context)
            text_content = render_to_string('calendar/email/event_update.txt', context)
            
            send_mail(
                subject=f'Updated: {event.name}',
                message=text_content,
                html_message=html_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[attendee.email],
                fail_silently=False,
            )
            
        except Exception:
            pass  # Log error in production