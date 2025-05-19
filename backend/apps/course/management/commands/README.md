# Course Management Commands

This directory contains Django management commands for the course module. Commands are now organized into logical groups for better maintainability.

## Command Structure

All commands are now grouped into three main files:
- `matching_commands.py` - All matching exercise related commands
- `testrecap_commands.py` - All test recap related commands  
- `course_maintenance.py` - Maintenance, diagnostic, and setup commands
- `speaking_auto_associate.py` - Speaking exercise commands (kept separate as it's simpler)

## Quick Start

### Complete Setup
```bash
# Run diagnostic first
poetry run python manage.py course_maintenance diagnostic --fix-suggestions

# Run complete setup for all lessons
poetry run python manage.py course_maintenance setup-all

# Setup specific lesson
poetry run python manage.py course_maintenance setup-all --lesson-id 1
```

### Common Tasks

#### Matching Exercises
```bash
# Create and associate matching exercises for all lessons
poetry run python manage.py matching_commands create

# Split large vocabulary lists into multiple smaller exercises
poetry run python manage.py matching_commands create --split --pairs-per-exercise 5

# Create exercises with custom settings
poetry run python manage.py matching_commands create --split --pairs-per-exercise 6 --lesson-id 1

# Associate vocabulary with existing exercises
poetry run python manage.py matching_commands associate --force

# Fix associations
poetry run python manage.py matching_commands fix --verbose
```

#### Test Recaps
```bash
# Complete setup - Creates ContentLesson, TestRecap, and Questions (RECOMMENDED)
poetry run python manage.py testrecap_commands setup --lesson-id 162

# Force recreate everything (deletes existing)
poetry run python manage.py testrecap_commands setup --lesson-id 162 --force

# Preview what would be created
poetry run python manage.py testrecap_commands setup --lesson-id 162 --dry-run

# Create test recaps (also creates ContentLesson by default)
poetry run python manage.py testrecap_commands create --lesson-id 162

# Create only TestRecap without ContentLesson
poetry run python manage.py testrecap_commands create --lesson-id 162 --no-content-lesson

# Debug test recap relationships
poetry run python manage.py testrecap_commands debug --lesson-id 162

# Show test recap information
poetry run python manage.py testrecap_commands show

# Fix schema issues and duplicates
poetry run python manage.py testrecap_commands fix-schema
```

#### Maintenance
```bash
# Run diagnostic check
poetry run python manage.py course_maintenance diagnostic

# Fix orphaned content
poetry run python manage.py course_maintenance fix-orphaned

# Run all setup commands
poetry run python manage.py course_maintenance setup-all
```

## Command Details

### matching_commands
Subcommands:
- `create` - Create and associate matching exercises
- `associate` - Associate vocabulary with existing exercises
- `fix` - Fix vocabulary associations

Options for `create`:
- `--split` - Split large vocabulary lists into multiple exercises
- `--pairs-per-exercise [N]` - Number of pairs per exercise when splitting (default: 5)
- `--pairs [N]` - Number of pairs for single exercise (default: 8)

Examples:
```bash
# Single exercise per lesson
poetry run python manage.py matching_commands create --dry-run

# Split into multiple exercises of 5 pairs each
poetry run python manage.py matching_commands create --split --pairs-per-exercise 5

# Create for specific lesson with 6 pairs per exercise
poetry run python manage.py matching_commands create --split --pairs-per-exercise 6 --lesson-id 1

# Associate vocabulary
poetry run python manage.py matching_commands associate --force --debug

# Fix associations  
poetry run python manage.py matching_commands fix --lesson-id 1 --verbose
```

### testrecap_commands
Subcommands:
- `setup` - Complete setup: creates ContentLesson, TestRecap, and generates questions (RECOMMENDED)
- `create` - Create test recaps (with optional ContentLesson)
- `create-content` - Create test recaps from existing content lessons
- `generate` - Generate questions for existing test recaps
- `show` - Display test recap information
- `debug` - Debug test recap relationships
- `fix-schema` - Fix schema issues and duplicates

Options:
- `--lesson-id [ID]` - Process specific lesson
- `--content-lesson-id [ID]` - Process specific content lesson (for create-content and debug)
- `--force` - Force recreation (for setup) or regeneration (for generate)
- `--dry-run` - Preview changes without applying them
- `--no-content-lesson` - Don't create ContentLesson (for create)

Examples:
```bash
# RECOMMENDED: Complete setup for a lesson
poetry run python manage.py testrecap_commands setup --lesson-id 162

# Force recreate everything (deletes existing)
poetry run python manage.py testrecap_commands setup --lesson-id 162 --force

# Preview what would be created
poetry run python manage.py testrecap_commands setup --lesson-id 162 --dry-run

# Create test recap (also creates ContentLesson by default)
poetry run python manage.py testrecap_commands create --lesson-id 162

# Create from existing ContentLesson  
poetry run python manage.py testrecap_commands create-content --content-lesson-id 92

# Debug relationships
poetry run python manage.py testrecap_commands debug --lesson-id 162
poetry run python manage.py testrecap_commands debug --content-lesson-id 92

# Show all test recaps or specific lesson
poetry run python manage.py testrecap_commands show
poetry run python manage.py testrecap_commands show --content-lesson-id 162
```

#### What Setup Creates
The `setup` command handles everything in one go:
1. Creates ContentLesson with type 'test_recap' if missing
2. Creates TestRecap for the lesson
3. Generates questions from lesson content:
   - Up to 5 vocabulary questions
   - Up to 3 matching exercises
   - Up to 3 fill in the blank exercises
   - Up to 3 multiple choice questions
   - Up to 2 speaking exercises

Each question type is assigned appropriate points (1-2) and ordered sequentially.

### course_maintenance
Subcommands:
- `diagnostic` - Run diagnostic checks
- `fix-orphaned` - Fix orphaned content lessons
- `setup-all` - Run all setup commands

Examples:
```bash
poetry run python manage.py course_maintenance diagnostic --fix-suggestions
poetry run python manage.py course_maintenance fix-orphaned --dry-run
poetry run python manage.py course_maintenance setup-all --skip-speaking
```

## Common Options

Most commands support these options:
- `--dry-run` - Preview changes without applying them
- `--force` - Force update even if data exists
- `--lesson-id [ID]` - Process specific lesson
- `--verbose` - Show detailed output

## Workflow Examples

### New Course Setup
```bash
# 1. Check current state
poetry run python manage.py course_maintenance diagnostic

# 2. Run complete setup
poetry run python manage.py course_maintenance setup-all

# 3. Verify results
poetry run python manage.py course_maintenance diagnostic
```

### Adding New Content
```bash
# After adding vocabulary to a lesson, setup everything in one command
poetry run python manage.py matching_commands create --lesson-id 5
poetry run python manage.py testrecap_commands setup --lesson-id 5
```

### Creating Test Recaps
```bash
# RECOMMENDED: Complete setup for a lesson
# Creates ContentLesson + TestRecap + Questions all at once
poetry run python manage.py testrecap_commands setup --lesson-id 162

# If you need to recreate/update an existing test recap
poetry run python manage.py testrecap_commands setup --lesson-id 162 --force

# Debug any issues
poetry run python manage.py testrecap_commands debug --lesson-id 162
```

### Fixing Issues
```bash
# Check for issues
poetry run python manage.py course_maintenance diagnostic --fix-suggestions

# Fix matching associations
poetry run python manage.py matching_commands fix --force

# Fix orphaned content
poetry run python manage.py course_maintenance fix-orphaned
```

## Getting Help

To see available subcommands and options:
```bash
poetry run python manage.py matching_commands --help
poetry run python manage.py testrecap_commands --help
poetry run python manage.py course_maintenance --help
```

For specific subcommand help:
```bash
poetry run python manage.py matching_commands create --help
```

## Test Recap Command Details

### Main Commands

1. **`setup`** (RECOMMENDED) - Complete one-command setup
   - Creates ContentLesson if missing
   - Creates TestRecap for the lesson
   - Generates questions automatically
   - Ensures "In Content" shows ✓ in admin

2. **`create`** - Creates TestRecap with optional ContentLesson
   - By default also creates ContentLesson
   - Use `--no-content-lesson` to skip ContentLesson creation
   - Best for manual control over the process

3. **`create-content`** - Creates TestRecap from existing ContentLesson
   - Use when you already have a ContentLesson with type='test_recap'
   - Preserves titles and descriptions from the ContentLesson

### Typical Workflow

```bash
# RECOMMENDED: One command does everything
poetry run python manage.py testrecap_commands setup --lesson-id 162

# Check the result
poetry run python manage.py testrecap_commands debug --lesson-id 162

# If you need to fix something
poetry run python manage.py testrecap_commands setup --lesson-id 162 --force
```

### Understanding "In Content" Status

The admin shows "In Content" ✓ when:
- A ContentLesson exists for the same lesson with `content_type='test_recap'`
- This is why `setup` and `create` commands now create ContentLesson by default

---

Last updated: 2025-05-19
Version: 2.2 (Simplified test recap commands with setup)