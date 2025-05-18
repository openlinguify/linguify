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
# Create test recaps
poetry run python manage.py testrecap_commands create

# Generate vocabulary questions
poetry run python manage.py testrecap_commands generate

# Update existing questions
poetry run python manage.py testrecap_commands update

# Show test recap information
poetry run python manage.py testrecap_commands show
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
- `create` - Create test recaps for vocabulary lessons
- `generate` - Generate questions for test recaps
- `update` - Update existing questions
- `show` - Display test recap information
- `fix-schema` - Fix schema issues

Examples:
```bash
poetry run python manage.py testrecap_commands create --lesson-id 1
poetry run python manage.py testrecap_commands generate --force
poetry run python manage.py testrecap_commands show --content-lesson-id 5
```

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

### Adding New Vocabulary
```bash
# After adding vocabulary to a lesson
poetry run python manage.py matching_commands create --lesson-id 5
poetry run python manage.py testrecap_commands generate --lesson-id 5
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

## Benefits of Grouped Commands

1. **Reduced File Count**: From 11 files to 4 files
2. **Logical Organization**: Related commands are grouped together
3. **Code Reuse**: Common functionality is shared within each file
4. **Easier Maintenance**: Less duplication, clearer structure
5. **Better Discovery**: Easier to find related commands

## Adding New Commands

When adding new functionality:
1. Determine which group it belongs to (matching, testrecap, or maintenance)
2. Add a new subcommand to the appropriate file
3. Update this README with the new command
4. Follow the existing pattern for command structure

---

Last updated: 2024
Version: 2.0 (Grouped Commands)