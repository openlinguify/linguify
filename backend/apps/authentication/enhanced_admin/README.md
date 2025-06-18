# Enhanced Admin Interface

This module contains admin enhancements that can be applied to the Linguify backend.

## Installation Instructions

1. First ensure your Django project is working correctly with the current admin interface.

2. Add the following code to the end of your `apps/authentication/admin.py` file:

```python
# Enhance the admin interface with additional features
try:
    from enhanced_admin.admin_enhancements import enhance_user_admin, enhance_coach_admin
    enhance_user_admin(UserAdmin)
    enhance_coach_admin(CoachProfileAdmin)
except ImportError:
    pass
```

3. Add the following URL pattern to your `core/urls.py` file:

```python
# Add admin dashboard
path('admin/stats/users/', include('enhanced_admin.urls')),
```

4. Run `python manage.py collectstatic` to ensure the template files are correctly recognized.

## Features

These enhancements add:

1. Advanced filters for user accounts (registration date, account status, profile completion)
2. Better visualization of account deletion status
3. Enhanced coach profile display with financial metrics
4. User statistics dashboard
5. Bulk export and notification features
6. And more!

## Troubleshooting

If you encounter any issues:

1. Make sure the enhanced_admin directory is in your project's Python path
2. Check that all templates are accessible 
3. Verify the Django admin is working correctly before applying enhancements