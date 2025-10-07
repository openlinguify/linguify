# -*- coding: utf-8 -*-
"""
Scheduling models for Linguify CMS
Complete appointment and availability management
"""
# Legacy models (keep for backward compatibility)
from ..models_old import PrivateLesson, TeacherSchedule

# New advanced models
from .availability import TeacherAvailability, RecurringAvailability, TimeSlot
from .appointment import Appointment, AppointmentType, BookingRequest
from .session import SessionNote, SessionFeedback
from .reminder import AppointmentReminder

__all__ = [
    # Legacy
    'PrivateLesson',
    'TeacherSchedule',

    # New models
    'TeacherAvailability',
    'RecurringAvailability',
    'TimeSlot',
    'Appointment',
    'AppointmentType',
    'BookingRequest',
    'SessionNote',
    'SessionFeedback',
    'AppointmentReminder',
]
