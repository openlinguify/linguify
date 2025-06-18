# PowerShell script to run dynamic system tests

Write-Host "🚀 Running Dynamic App Management System Tests" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Set test settings
$env:DJANGO_SETTINGS_MODULE = "core.settings_test"

# Run the tests
Write-Host "Running manifest parser tests..." -ForegroundColor Yellow
python manage.py test tests.test_public_web_dynamic_system --verbosity=2

Write-Host "Running views tests..." -ForegroundColor Yellow  
python manage.py test tests.test_public_web_views --verbosity=2

Write-Host "Running templatetags tests..." -ForegroundColor Yellow
python manage.py test tests.test_public_web_templatetags --verbosity=2

Write-Host "Running integration tests..." -ForegroundColor Yellow
python manage.py test tests.test_public_web_integration --verbosity=2

Write-Host "✅ All dynamic system tests completed!" -ForegroundColor Green