# PowerShell script to test specific fixes

Write-Host "🔧 Testing Dynamic System Fixes" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green

$env:DJANGO_SETTINGS_MODULE = "core.settings_test"

Write-Host "Testing template tags..." -ForegroundColor Yellow
python manage.py test tests.test_public_web_templatetags.TemplateTagRegistrationTest.test_template_tags_are_registered --verbosity=2

Write-Host "Testing views..." -ForegroundColor Yellow  
python manage.py test tests.test_public_web_views.PublicWebViewsTest.test_landing_view --verbosity=2
python manage.py test tests.test_public_web_views.PublicWebLanguageTest --verbosity=2

Write-Host "Testing integration..." -ForegroundColor Yellow
python manage.py test tests.test_public_web_integration.URLRoutingIntegrationTest.test_multilingual_urls --verbosity=2
python manage.py test tests.test_public_web_integration.PerformanceIntegrationTest.test_caching_behavior --verbosity=2
python manage.py test tests.test_public_web_integration.SecurityIntegrationTest.test_template_security --verbosity=2

Write-Host "✅ Fix testing completed!" -ForegroundColor Green