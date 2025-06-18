# Test Scripts for Matching Exercises

This directory contains test scripts for debugging and testing matching exercise functionality.

## Available Scripts

### 1. test_matching_association.py

Tests the matching exercise vocabulary association functionality.

Usage:
```bash
cd /mnt/c/Users/louis/WebstormProjects/linguify/backend
poetry run python manage.py shell < scripts/tests/test_matching_association.py
```

This script will:
- Find lessons with vocabulary
- Check matching exercises
- Test vocabulary association
- Display results

### 2. debug_content_type.py

Debugs content type values in the database.

Usage:
```bash
cd /mnt/c/Users/louis/WebstormProjects/linguify/backend
poetry run python manage.py shell < scripts/tests/debug_content_type.py
```

This script will:
- Show all unique content types
- Display content types for specific lessons
- Show ContentLesson choices
- Help diagnose content type issues

## Running Tests

Always run these scripts from the Django shell to have access to the models:

```bash
poetry run python manage.py shell < scripts/tests/[script_name].py
```

## Adding New Test Scripts

Place any new test scripts in this directory and update this README.