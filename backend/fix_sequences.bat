@echo off
echo Fixing PostgreSQL sequences...
echo.
echo Please run the following SQL commands when the PostgreSQL prompt appears:
echo.
echo SELECT setval('django_content_type_id_seq', (SELECT MAX(id) FROM django_content_type) + 1);
echo SELECT setval('auth_permission_id_seq', (SELECT MAX(id) FROM auth_permission) + 1);
echo \q
echo.
echo Press any key to open database shell...
pause > nul
python manage.py dbshell