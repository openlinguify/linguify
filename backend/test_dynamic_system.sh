#!/bin/bash
# Script to run dynamic system tests

echo "🚀 Running Dynamic App Management System Tests"
echo "=================================================="

# Set test settings
export DJANGO_SETTINGS_MODULE=core.settings_test

# Run the tests
echo "Running manifest parser tests..."
python manage.py test tests.test_public_web_dynamic_system --verbosity=2

echo "Running views tests..."
python manage.py test tests.test_public_web_views --verbosity=2

echo "Running templatetags tests..."
python manage.py test tests.test_public_web_templatetags --verbosity=2

echo "Running integration tests..."
python manage.py test tests.test_public_web_integration --verbosity=2

echo "✅ All dynamic system tests completed!"