# Jobs Management System for Linguify

This module provides a comprehensive job management system for Linguify's careers page. It's designed to be private and not included in the open-source distribution.

## 🔒 Private Module Notice

**This module should NOT be included in the open-source repository.** It contains sensitive business information and recruitment data.

## 🚀 Setup Instructions

### 1. Add to Django Settings

Add the jobs app to your `INSTALLED_APPS` in `backend/core/settings.py`:

```python
INSTALLED_APPS = [
    # ... other apps
    'apps.jobs',
]
```

### 2. Add URL Configuration

Add to your main `backend/core/urls.py`:

```python
urlpatterns = [
    # ... other patterns
    path('api/v1/jobs/', include('apps.jobs.urls', namespace='jobs')),
]
```

### 3. Run Migrations

```bash
cd backend
python manage.py makemigrations jobs
python manage.py migrate
```

### 4. Create Superuser (if not already done)

```bash
python manage.py createsuperuser
```

## 📊 Admin Interface

Access the admin interface at `/admin/` to manage:

### Departments
- Create departments (Engineering, Product, Marketing, etc.)
- Track number of active positions per department

### Job Positions
- **Basic Info**: Title, department, location, employment type
- **Details**: Description, requirements, responsibilities, benefits
- **Salary**: Optional salary range
- **Application**: Email and optional URL for applications
- **Status**: Active/inactive, featured positions
- **Dates**: Posted date, optional closing date

### Job Applications
- View all applications
- Track application status (submitted, reviewed, interview, etc.)
- Add internal notes
- Filter by position, department, status

## 🎯 Features

### For Administrators
- **Rich Admin Interface**: Easy-to-use Django admin with custom actions
- **Application Tracking**: Full applicant lifecycle management
- **Filtering & Search**: Find positions and applications quickly
- **Status Management**: Bulk actions for positions and applications
- **Analytics**: View application counts and breakdowns

### For Website Visitors
- **Dynamic Job Listings**: Real-time job positions from database
- **Department Filtering**: Filter jobs by department
- **Featured Positions**: Highlight important roles
- **Detailed Information**: Full job descriptions, requirements, benefits
- **Application Integration**: Direct links to application forms

## 🔧 API Endpoints

### Public Endpoints (No Authentication Required)

```
GET /api/v1/jobs/departments/          # List all departments
GET /api/v1/jobs/positions/            # List active positions
GET /api/v1/jobs/positions/{id}/       # Get position details
POST /api/v1/jobs/apply/               # Submit application
GET /api/v1/jobs/stats/                # General statistics
```

### Filtering Options

```
GET /api/v1/jobs/positions/?department=1
GET /api/v1/jobs/positions/?employment_type=full_time
GET /api/v1/jobs/positions/?search=python
```

## 📝 Adding Job Positions

### Via Admin Interface (Recommended)

1. Go to `/admin/jobs/jobposition/`
2. Click "Add Job Position"
3. Fill in all required fields:
   - Title
   - Department
   - Location
   - Description
   - Requirements
   - Application email
4. Set status (active/featured)
5. Save

### Example Job Position

```
Title: Senior Python Developer
Department: Engineering
Location: Paris, France (Remote possible)
Employment Type: Full Time
Experience Level: Senior

Description:
We're looking for a senior Python developer to join our engineering team...

Requirements:
- 5+ years of Python experience
- Experience with Django/FastAPI
- Knowledge of PostgreSQL
- Experience with AWS/Docker

Responsibilities:
- Develop and maintain backend services
- Code review and mentoring
- Architecture decisions
- API design and implementation

Application Email: jobs@linguify.com
```

## 🔄 Frontend Integration

The careers page (`/careers`) automatically:
- Loads positions from the API
- Shows department filtering
- Displays featured badges
- Handles loading states
- Shows "no positions" message when empty

## 🚫 Excluding from Open Source

### Option 1: .gitignore (Recommended)

Add to your `.gitignore`:

```
# Private job management system
backend/apps/jobs/
frontend/src/core/api/jobsApi.ts
```

### Option 2: Private Fork

Maintain this module in a private fork or separate repository that gets pulled into production deployments.

### Option 3: Environment Toggle

Add to `settings.py`:

```python
# Only include jobs app in production
if os.environ.get('ENABLE_JOBS_MODULE', 'false').lower() == 'true':
    INSTALLED_APPS.append('apps.jobs')
```

## 🧪 Testing

Run tests:

```bash
python manage.py test apps.jobs
```

Tests cover:
- Model functionality
- API endpoints
- Application submission
- Data validation

## 🔐 Security Considerations

- **No Authentication Required**: Public API for job listings
- **Admin Only**: Job management requires superuser access
- **Input Validation**: All user inputs are validated
- **Email Protection**: Application emails are not exposed in listings
- **Rate Limiting**: Consider adding rate limiting for application submissions

## 📞 Support

For questions about this system, contact the development team internally.

**Remember: This module contains sensitive business data and should remain private.**