# Account Deletion System

Linguify implements a GDPR-compliant account deletion system that gives users the option to either delete their account immediately or schedule deletion with a 30-day grace period, allowing them to change their mind during this time.

## Features

### Two Deletion Options

1. **Temporary Deletion (30-day grace period)**
   - Account is immediately deactivated but not permanently deleted
   - User has 30 days to restore their account
   - Email reminder is sent 3 days before permanent deletion
   - After 30 days, the account is permanently deleted

2. **Permanent Deletion (Immediate)**
   - Account is immediately and permanently deleted
   - Personal data is anonymized for GDPR compliance
   - This action cannot be undone

### Account Recovery

- Users can recover their account during the 30-day grace period
- Recovery page is accessible at `/account-recovery`
- Recovering an account reactivates it with all data intact

## Technical Implementation

### Database Schema

The User model has been extended with the following fields:

```python
# Fields for tracking account deletion with 30-day grace period
is_pending_deletion = models.BooleanField(default=False)
deletion_scheduled_at = models.DateTimeField(null=True, blank=True)
deletion_date = models.DateTimeField(null=True, blank=True)
```

### Key Methods

- `schedule_account_deletion(days_retention=30)`: Marks an account for deletion after the specified period
- `cancel_account_deletion()`: Cancels scheduled deletion and reactivates account
- `delete_user_account(anonymize=True, immediate=False)`: Deletes account, with options for anonymization and immediate deletion
- `days_until_deletion()`: Calculates days remaining until permanent deletion

### API Endpoints

- `POST /api/auth/delete-account/`: Delete user account (temporary or permanent)
- `POST /api/auth/restore-account/`: Restore an account scheduled for deletion

### Scheduled Task

A daily task processes accounts scheduled for deletion:

1. Permanently deletes accounts that have reached their deletion date
2. Sends reminder emails 3 days before permanent deletion

This is implemented as a Django management command:

```bash
python manage.py process_deleted_accounts
```

For production deployment, this command should be scheduled to run daily using cron or a similar scheduler.

## Testing the Feature

### Manual Testing

1. **Test Temporary Deletion**:
   - Log in as a test user
   - Go to Settings > Danger Zone
   - Click "Delete Account" and select "Temporary Deletion"
   - Confirm deletion
   - Verify you are logged out and redirected to account-deleted page
   - Try to log in again (should fail as account is deactivated)
   - Go to /account-recovery and log in
   - Restore the account
   - Verify you can now log in successfully

2. **Test Permanent Deletion**:
   - Log in as a test user
   - Go to Settings > Danger Zone
   - Click "Delete Account" and select "Permanent Deletion"
   - Confirm deletion
   - Verify you are logged out and redirected to account-deleted page
   - Try to log in again (should fail as account is deleted)

### Testing the Scheduled Task

To test the scheduled deletion task:

```bash
# Test with dry-run (no changes)
python manage.py process_deleted_accounts --dry-run

# Actually process deletions
python manage.py process_deleted_accounts
```

For testing email reminders, you can manually set a user's `deletion_date` to 3 days from now:

```python
from django.utils import timezone
import datetime
from apps.authentication.models import User

user = User.objects.get(email='test@example.com')
user.is_pending_deletion = True
user.deletion_scheduled_at = timezone.now()
user.deletion_date = timezone.now() + datetime.timedelta(days=3)
user.is_active = False
user.save()
```

Then run the management command to trigger the reminder email.

## Production Setup

For production, add a cron job that runs the command daily:

```
0 0 * * * cd /path/to/linguify/backend && /path/to/python manage.py process_deleted_accounts >> /var/log/linguify/deletion.log 2>&1
```

If using Docker, the provided `docker-compose.override.yml` file includes a scheduled-tasks service that handles this automatically.