"""
Tests for calendar management commands
"""
from datetime import datetime, timedelta
from io import StringIO
from unittest.mock import patch, MagicMock
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.utils import timezone

from ..models import CalendarEvent, CalendarAttendee
from ..management.commands.send_calendar_reminders import Command as RemindersCommand
from ..management.commands.send_daily_agenda import Command as AgendaCommand

User = get_user_model()


class SendCalendarRemindersCommandTest(TestCase):
    """Test send_calendar_reminders management command"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create event in reminder window (15 minutes from now)
        self.upcoming_event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Upcoming Meeting',
            start=timezone.now() + timedelta(minutes=15),
            stop=timezone.now() + timedelta(minutes=75),
            active=True
        )
        
        # Create event outside reminder window (2 hours from now)
        self.future_event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Future Meeting',
            start=timezone.now() + timedelta(hours=2),
            stop=timezone.now() + timedelta(hours=3),
            active=True
        )
    
    def test_command_dry_run_mode(self):
        """Test command in dry run mode"""
        out = StringIO()
        
        call_command(
            'send_calendar_reminders',
            '--dry-run',
            '--verbose',
            stdout=out
        )
        
        output = out.getvalue()
        
        # Should show dry run mode
        self.assertIn('DRY RUN MODE', output)
        self.assertIn('Found', output)
        self.assertIn('events in reminder window', output)
    
    @patch('apps.calendar_app.signals.check_and_send_event_reminders')
    def test_command_normal_mode(self, mock_check_reminders):
        """Test command in normal mode"""
        mock_check_reminders.return_value = 1
        
        out = StringIO()
        
        call_command(
            'send_calendar_reminders',
            '--verbose',
            stdout=out
        )
        
        output = out.getvalue()
        
        # Should not show dry run mode
        self.assertNotIn('DRY RUN MODE', output)
        self.assertIn('Successfully processed 1 event reminders', output)
        
        # Should call actual reminder function
        mock_check_reminders.assert_called_once()
    
    def test_command_no_reminders_verbose(self):
        """Test command with no reminders and verbose output"""
        # Delete all events
        CalendarEvent.objects.all().delete()
        
        out = StringIO()
        
        call_command(
            'send_calendar_reminders',
            '--dry-run',
            '--verbose',
            stdout=out
        )
        
        output = out.getvalue()
        
        self.assertIn('Found 0 events in reminder window', output)
        self.assertIn('No events need reminders', output)
    
    def test_command_no_reminders_quiet(self):
        """Test command with no reminders and no verbose output"""
        # Delete all events
        CalendarEvent.objects.all().delete()
        
        out = StringIO()
        
        call_command(
            'send_calendar_reminders',
            '--dry-run',
            stdout=out
        )
        
        output = out.getvalue()
        
        # Should not show detailed info without verbose
        self.assertNotIn('No events need reminders', output)
    
    @patch('apps.calendar_app.signals.check_and_send_event_reminders')
    def test_command_handles_errors(self, mock_check_reminders):
        """Test that command handles errors gracefully"""
        mock_check_reminders.side_effect = Exception("Test error")
        
        out = StringIO()
        err = StringIO()
        
        with self.assertRaises(Exception):
            call_command(
                'send_calendar_reminders',
                stdout=out,
                stderr=err
            )
        
        output = out.getvalue()
        self.assertIn('Error sending calendar reminders', output)
    
    def test_command_class_directly(self):
        """Test command class directly"""
        command = RemindersCommand()
        
        # Test help text
        self.assertEqual(
            command.help,
            'Send reminder notifications for upcoming calendar events'
        )
        
        # Test with dry run
        out = StringIO()
        command.stdout = out
        
        command.handle(dry_run=True, verbose=True)
        
        output = out.getvalue()
        self.assertIn('DRY RUN MODE', output)


class SendDailyAgendaCommandTest(TestCase):
    """Test send_daily_agenda management command"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create event for today
        today_start = timezone.now().replace(hour=10, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(hours=1)
        
        self.today_event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Today Meeting',
            start=today_start,
            stop=today_end,
            active=True
        )
        
        # Create event for tomorrow
        tomorrow_start = timezone.now() + timedelta(days=1)
        tomorrow_end = tomorrow_start + timedelta(hours=1)
        
        self.tomorrow_event = CalendarEvent.objects.create(
            user_id=self.user,
            name='Tomorrow Meeting',
            start=tomorrow_start,
            stop=tomorrow_end,
            active=True
        )
    
    def test_command_dry_run_mode(self):
        """Test command in dry run mode"""
        out = StringIO()
        
        call_command(
            'send_daily_agenda',
            '--dry-run',
            '--verbose',
            stdout=out
        )
        
        output = out.getvalue()
        
        # Should show dry run mode
        self.assertIn('DRY RUN MODE', output)
        self.assertIn('Found', output)
        self.assertIn('users with events today', output)
    
    @patch('apps.calendar_app.signals.send_daily_agenda_notifications')
    def test_command_normal_mode(self, mock_send_agenda):
        """Test command in normal mode"""
        mock_send_agenda.return_value = 1
        
        out = StringIO()
        
        call_command(
            'send_daily_agenda',
            '--verbose',
            stdout=out
        )
        
        output = out.getvalue()
        
        # Should not show dry run mode
        self.assertNotIn('DRY RUN MODE', output)
        self.assertIn('Successfully sent 1 daily agendas', output)
        
        # Should call actual agenda function
        mock_send_agenda.assert_called_once()
    
    def test_command_with_specific_date(self):
        """Test command with specific date parameter"""
        out = StringIO()
        
        # Use tomorrow's date
        tomorrow = (timezone.now() + timedelta(days=1)).date()
        
        call_command(
            'send_daily_agenda',
            '--dry-run',
            '--verbose',
            '--date', tomorrow.strftime('%Y-%m-%d'),
            stdout=out
        )
        
        output = out.getvalue()
        
        self.assertIn(f'Starting daily agenda for {tomorrow}', output)
    
    def test_command_invalid_date_format(self):
        """Test command with invalid date format"""
        out = StringIO()
        
        call_command(
            'send_daily_agenda',
            '--date', 'invalid-date',
            stdout=out
        )
        
        output = out.getvalue()
        self.assertIn('Invalid date format', output)
    
    def test_command_no_events_verbose(self):
        """Test command with no events today and verbose output"""
        # Delete today's events
        self.today_event.delete()
        
        out = StringIO()
        
        call_command(
            'send_daily_agenda',
            '--dry-run',
            '--verbose',
            stdout=out
        )
        
        output = out.getvalue()
        
        self.assertIn('Found 0 users with events today', output)
        self.assertIn('No users have events today', output)
    
    def test_command_no_events_quiet(self):
        """Test command with no events today and no verbose output"""
        # Delete today's events
        self.today_event.delete()
        
        out = StringIO()
        
        call_command(
            'send_daily_agenda',
            '--dry-run',
            stdout=out
        )
        
        output = out.getvalue()
        
        # Should not show detailed info without verbose
        self.assertNotIn('No users have events today', output)
    
    @patch('apps.calendar_app.signals.send_daily_agenda_notifications')
    def test_command_handles_errors(self, mock_send_agenda):
        """Test that command handles errors gracefully"""
        mock_send_agenda.side_effect = Exception("Test error")
        
        out = StringIO()
        err = StringIO()
        
        with self.assertRaises(Exception):
            call_command(
                'send_daily_agenda',
                stdout=out,
                stderr=err
            )
        
        output = out.getvalue()
        self.assertIn('Error sending daily agendas', output)
    
    def test_command_class_directly(self):
        """Test command class directly"""
        command = AgendaCommand()
        
        # Test help text
        self.assertEqual(
            command.help,
            'Send daily agenda notifications to users with events today'
        )
        
        # Test with dry run
        out = StringIO()
        command.stdout = out
        
        command.handle(dry_run=True, verbose=True, date=None)
        
        output = out.getvalue()
        self.assertIn('DRY RUN MODE', output)


class CommandIntegrationTest(TestCase):
    """Integration tests for management commands"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='user1',
            email='user1@example.com',
            password='testpass123'
        )
        
        self.user2 = User.objects.create_user(
            username='user2',
            email='user2@example.com',
            password='testpass123'
        )
    
    def test_commands_with_multiple_users_and_events(self):
        """Test commands with multiple users and events"""
        # Create events for both users
        
        # User 1: event in reminder window and event today
        CalendarEvent.objects.create(
            user_id=self.user1,
            name='User1 Reminder Event',
            start=timezone.now() + timedelta(minutes=15),
            stop=timezone.now() + timedelta(minutes=75),
            active=True
        )
        
        today_start = timezone.now().replace(hour=14, minute=0, second=0, microsecond=0)
        CalendarEvent.objects.create(
            user_id=self.user1,
            name='User1 Today Event',
            start=today_start,
            stop=today_start + timedelta(hours=1),
            active=True
        )
        
        # User 2: only event today
        today_start2 = timezone.now().replace(hour=16, minute=0, second=0, microsecond=0)
        CalendarEvent.objects.create(
            user_id=self.user2,
            name='User2 Today Event',
            start=today_start2,
            stop=today_start2 + timedelta(hours=1),
            active=True
        )
        
        # Test reminder command
        out1 = StringIO()
        call_command(
            'send_calendar_reminders',
            '--dry-run',
            '--verbose',
            stdout=out1
        )
        
        output1 = out1.getvalue()
        self.assertIn('Found 1 events in reminder window', output1)
        
        # Test agenda command
        out2 = StringIO()
        call_command(
            'send_daily_agenda',
            '--dry-run',
            '--verbose',
            stdout=out2
        )
        
        output2 = out2.getvalue()
        self.assertIn('Found 2 users with events today', output2)
    
    def test_commands_with_inactive_events(self):
        """Test that commands ignore inactive events"""
        # Create inactive event in reminder window
        CalendarEvent.objects.create(
            user_id=self.user1,
            name='Inactive Event',
            start=timezone.now() + timedelta(minutes=15),
            stop=timezone.now() + timedelta(minutes=75),
            active=False  # Inactive
        )
        
        # Create inactive event today
        today_start = timezone.now().replace(hour=12, minute=0, second=0, microsecond=0)
        CalendarEvent.objects.create(
            user_id=self.user1,
            name='Inactive Today Event',
            start=today_start,
            stop=today_start + timedelta(hours=1),
            active=False  # Inactive
        )
        
        # Test reminder command
        out1 = StringIO()
        call_command(
            'send_calendar_reminders',
            '--dry-run',
            '--verbose',
            stdout=out1
        )
        
        output1 = out1.getvalue()
        self.assertIn('Found 0 events in reminder window', output1)
        
        # Test agenda command
        out2 = StringIO()
        call_command(
            'send_daily_agenda',
            '--dry-run',
            '--verbose',
            stdout=out2
        )
        
        output2 = out2.getvalue()
        self.assertIn('Found 0 users with events today', output2)
    
    def test_commands_output_formatting(self):
        """Test that command output is properly formatted"""
        out = StringIO()
        
        call_command(
            'send_calendar_reminders',
            '--dry-run',
            stdout=out
        )
        
        output = out.getvalue()
        
        # Should start with timestamp and completion message
        self.assertIn('Starting calendar reminder check', output)
        self.assertIn('Calendar reminder check completed', output)
        
        # Test agenda command formatting
        out2 = StringIO()
        
        call_command(
            'send_daily_agenda',
            '--dry-run',
            stdout=out2
        )
        
        output2 = out2.getvalue()
        
        self.assertIn('Starting daily agenda', output2)
        self.assertIn('Daily agenda processing completed', output2)


class CommandArgumentsTest(TestCase):
    """Test command argument parsing and validation"""
    
    def test_reminder_command_arguments(self):
        """Test reminder command argument handling"""
        command = RemindersCommand()
        
        # Test argument parser setup
        parser = command.create_parser('test', 'send_calendar_reminders')
        
        # Test dry-run argument
        args = parser.parse_args(['--dry-run'])
        self.assertTrue(args.dry_run)
        
        # Test verbose argument
        args = parser.parse_args(['--verbose'])
        self.assertTrue(args.verbose)
        
        # Test both arguments
        args = parser.parse_args(['--dry-run', '--verbose'])
        self.assertTrue(args.dry_run)
        self.assertTrue(args.verbose)
    
    def test_agenda_command_arguments(self):
        """Test agenda command argument handling"""
        command = AgendaCommand()
        
        # Test argument parser setup
        parser = command.create_parser('test', 'send_daily_agenda')
        
        # Test date argument
        args = parser.parse_args(['--date', '2025-08-19'])
        self.assertEqual(args.date, '2025-08-19')
        
        # Test all arguments together
        args = parser.parse_args(['--dry-run', '--verbose', '--date', '2025-08-19'])
        self.assertTrue(args.dry_run)
        self.assertTrue(args.verbose)
        self.assertEqual(args.date, '2025-08-19')
    
    def test_command_help_text(self):
        """Test that commands have proper help text"""
        # Test reminder command help
        out = StringIO()
        
        call_command(
            'send_calendar_reminders',
            '--help',
            stdout=out
        )
        
        help_output = out.getvalue()
        self.assertIn('Send reminder notifications', help_output)
        self.assertIn('--dry-run', help_output)
        self.assertIn('--verbose', help_output)
        
        # Test agenda command help
        out2 = StringIO()
        
        call_command(
            'send_daily_agenda',
            '--help',
            stdout=out2
        )
        
        help_output2 = out2.getvalue()
        self.assertIn('Send daily agenda notifications', help_output2)
        self.assertIn('--date', help_output2)