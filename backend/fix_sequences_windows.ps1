# PowerShell script to fix PostgreSQL sequences

# Load environment variables from .env file if it exists
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match '^([^=]+)=(.*)$') {
            [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
        }
    }
}

# Run the Django management command to access the database shell
Write-Host "Fixing PostgreSQL sequences..."
Write-Host "This will run SQL commands to fix the sequence issues."

# Option 1: Using Django dbshell (recommended)
python manage.py dbshell -c @"
-- Fix django_content_type sequence
SELECT setval(pg_get_serial_sequence('django_content_type', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM django_content_type;

-- Fix auth_permission sequence  
SELECT setval(pg_get_serial_sequence('auth_permission', 'id'), COALESCE(MAX(id), 0) + 1, false) FROM auth_permission;

-- Show result
SELECT 'Sequences fixed successfully' as result;
"@

Write-Host "Done! You can now run migrations again."