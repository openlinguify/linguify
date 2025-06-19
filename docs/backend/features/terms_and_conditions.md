# Terms and Conditions Acceptance System

Linguify includes a robust terms and conditions acceptance system to ensure legal compliance and provide a clear record of user acceptance.

## Overview

The terms and conditions system ensures that:

1. New users are required to accept terms before using the application
2. Existing users are notified when terms are updated and need to accept the new version
3. Administrators can track who has accepted terms and when
4. Users who have not accepted terms are limited in functionality

## User Model Fields

The system adds the following fields to the User model:

- `terms_accepted` (boolean): Whether the user has accepted the terms and conditions
- `terms_accepted_at` (datetime): When the user accepted the terms
- `terms_version` (string): The version of the terms that was accepted

## API Endpoints

The following API endpoints manage terms acceptance:

- `GET /api/auth/terms/status`: Get the current user's terms acceptance status
- `POST /api/auth/terms/accept`: Accept the terms and conditions

## Frontend Components

The system includes the following frontend components:

- `TermsAcceptance`: A modal dialog for accepting terms
- `TermsNotification`: A notification banner for users who need to accept terms
- `useTermsGuard`: A hook for protecting routes requiring terms acceptance
- `withTermsAcceptance`: A higher-order component to wrap protected pages

## Administrator Tools

Administrators have several tools for managing terms acceptance:

### Django Admin Interface

The admin interface includes:

- Terms acceptance status display in the user list
- Filtering users by terms acceptance status
- A dedicated section for viewing and editing terms acceptance fields

### Management Commands

The following management commands are available:

#### Update Terms Fields

```bash
# Accept terms for all users
python manage.py update_terms_fields --accept

# Accept terms for a specific user
python manage.py update_terms_fields --user-email=user@example.com --accept

# Clear terms acceptance for all users
python manage.py update_terms_fields --clear

# Set a specific terms version
python manage.py update_terms_fields --accept --version=v1.1
```

#### Terms Statistics

```bash
# View terms acceptance statistics
python manage.py terms_statistics

# Export statistics to CSV
python manage.py terms_statistics --export=stats.csv

# Statistics for the last 60 days
python manage.py terms_statistics --days=60
```

### Automated Tasks

The system includes automated tasks for terms compliance:

- `remind_users_to_accept_terms`: Sends email reminders to users who haven't accepted terms
- `check_terms_compliance`: Generates and distributes a compliance report to administrators

## Implementation Details

### Database Migration

The database migration `0015_user_terms_acceptance.py` adds the required fields to the User model.

### Authentication Flow

1. When a user registers or logs in, the system checks their terms acceptance status
2. If terms have not been accepted, they are redirected or shown the terms acceptance modal
3. Once terms are accepted, the acceptance is recorded with timestamp and version

### Versioning

The system supports versioning of terms:

- When terms are updated, the version can be incremented (e.g., "v1.0" to "v1.1")
- Users must accept the new version when it changes
- The system records which version of the terms each user has accepted

## Best Practices

- Always run the database migration before deploying the terms system
- Update the terms page at `/annexes/legal` when terms change
- Increment the terms version when making material changes
- Regularly review terms compliance reports
- Inform users in advance when terms will be updated