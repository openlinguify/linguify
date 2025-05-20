# Course Management Commands

This directory contains Django management commands for the course module. Commands are now organized into logical groups for better maintainability.

## Command Structure

All commands are now grouped into main files:
- `matching_commands.py` - All matching exercise related commands
- `testrecap_commands.py` - All test recap related commands  
- `course_maintenance.py` - Maintenance, diagnostic, and setup commands
- `create_smart_theory_lesson.py` - Theory content creation with templates
- `analyze_missing_theory.py` - Find and create missing theory content
- `speaking_auto_associate.py` - Speaking exercise commands (kept separate as it's simpler)
- `split_vocabulary_lesson.py` - Split large vocabulary lessons into multiple parts

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

#### Vocabulary Lesson Splitting (Look at the id of contend lesson)
```bash
# Preview splitting a vocabulary lesson into parts
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --dry-run --interactive

# Split with specific number of parts 
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --parts=3 --dry-run

# Split to different target units
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --target-unit-id=15 --dry-run

# Split to multiple different target units
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --parts=3 --target-units=15,22 --dry-run

# Manual selection of words per part
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --parts=3 --interactive --manual-selection

# Complete example with all options 
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --parts=3 --target-units=15,22 --interactive --manual-selection
```

#### Theory Content
```bash
# Preview what would be created for a lesson
poetry run python manage.py create_smart_theory_lesson --lesson-id 12 --auto-title --dry-run

# Create theory with automatic title detection
poetry run python manage.py create_smart_theory_lesson --lesson-id 12 --auto-title

# Use a specific template
poetry run python manage.py create_smart_theory_lesson --lesson-id 45 --template articles

# List all available templates
poetry run python manage.py create_smart_theory_lesson --list-templates

# Analyze missing theory content
poetry run python manage.py analyze_missing_theory

# Analyze specific unit
poetry run python manage.py analyze_missing_theory --unit 6

# Create all missing theory content
poetry run python manage.py analyze_missing_theory --create

# Generate detailed theory report
poetry run python manage.py analyze_missing_theory --report

# Check for duplicate theories
poetry run python manage.py analyze_missing_theory --check-duplicates

# Preview what would be created
poetry run python manage.py analyze_missing_theory --create --dry-run
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

### split_vocabulary_lesson
Splits large vocabulary lessons into multiple parts with intelligent numbering.

Options:
- `--lesson-id [ID]` - ID of the vocabulary content lesson to split (required)
- `--parts [N]` - Number of parts to create (if not specified, calculated automatically)
- `--min-words [N]` - Minimum words required to consider splitting (default: 20)
- `--optimal-words [N]` - Optimal number of words per sub-lesson (default: 12)
- `--target-unit-id [ID]` - ID of unit where to place new lessons (default: same as source)
- `--target-units [IDS]` - Comma-separated list of unit IDs for parts 2,3,etc. (e.g., "15,22")
- `--interactive` - Interactive mode to validate each decision
- `--manual-selection` - Enable manual selection of words for each part (requires --interactive)
- `--thematic` - Try to group by theme/similarity
- `--keep-original` - Keep the original lesson title unchanged
- `--create-matching` - Create matching exercises for the new lessons
- `--reorganize` - Reorganize lesson orders after division
- `--dry-run` - Simulate execution without applying changes
- `--export-words [FILE]` - Export the divided words to a CSV file for validation
- `--import-validation [FILE]` - Import a CSV validation file with word distribution
- `--auto-optimize` - Calculate optimal number of divisions automatically

Examples:
```bash
# Basic usage with interactive mode
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --dry-run --interactive

# Split with specific number of parts
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --parts=3 --dry-run

# Split to different target unit
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --target-unit-id=15 --dry-run

# Split to multiple different target units
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --parts=3 --target-units=15,22 --dry-run

# Manual selection of words per part with interactive mode
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --parts=3 --interactive --manual-selection

# Export words for manual validation
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --export-words=lesson_151_words.csv

# Import validated word distribution
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --import-validation=lesson_151_words.csv

# Create with thematic grouping and matching exercises
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --thematic --create-matching
```

#### Intelligent Lesson Numbering

The command uses smart numbering for lessons:
- If splitting "Animals" for the first time, creates "Animals 1" and "Animals 2"
- If "Animals 1" already exists, creates "Animals 2", "Animals 3", etc.
- If "Animals 1" and "Animals 3" exist, creates "Animals 2", "Animals 4", etc.

#### Manual Selection Mode

When using `--interactive --manual-selection`:
- Displays all vocabulary words with indices
- Allows selection using individual indices (1,3,5) or ranges (1-5)
- Provides commands to view, cancel, or automatically distribute words
- Automatically assigns any remaining words to the last part
- Shows statistics about the distribution balance

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

### create_smart_theory_lesson
Creates theory content with intelligent title detection and template selection.

Options:
- `--lesson-id [ID]` - Lesson ID where to add the theory content (required)
- `--auto-title` - Automatically detect title from lesson context
- `--title [TITLE]` - Manual title override
- `--template [NAME]` - Use specific template (dates, articles, etc.)
- `--order [N]` - Order in the lesson
- `--dry-run` - Preview what would be created without creating
- `--list-templates` - List all available templates

Examples:
```bash
# Preview creation with auto-detected title
poetry run python manage.py create_smart_theory_lesson --lesson-id 12 --auto-title --dry-run

# Create with auto-detected title and template
poetry run python manage.py create_smart_theory_lesson --lesson-id 12 --auto-title

# Use specific template
poetry run python manage.py create_smart_theory_lesson --lesson-id 45 --template articles

# Manual title and order
poetry run python manage.py create_smart_theory_lesson --lesson-id 78 --title "Les Pronoms" --order 3

# See available templates
poetry run python manage.py create_smart_theory_lesson --list-templates
```

### analyze_missing_theory
Finds lessons without theory content and optionally creates it.

Options:
- `--unit [ID]` - Filter by specific unit
- `--create` - Create theory for all missing lessons
- `--dry-run` - Preview what would be created
- `--report` - Generate detailed report with statistics
- `--check-duplicates` - Check for duplicate theories

Examples:
```bash
# Show all lessons without theory
poetry run python manage.py analyze_missing_theory

# Check specific unit
poetry run python manage.py analyze_missing_theory --unit 6

# Create theory for all missing lessons
poetry run python manage.py analyze_missing_theory --create

# Preview what would be created
poetry run python manage.py analyze_missing_theory --create --dry-run

# Generate detailed report
poetry run python manage.py analyze_missing_theory --report

# Check for duplicate theories
poetry run python manage.py analyze_missing_theory --check-duplicates
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

### Adding New Content
```bash
# After adding vocabulary to a lesson, setup everything in one command
poetry run python manage.py matching_commands create --lesson-id 5
poetry run python manage.py testrecap_commands setup --lesson-id 5
# Add theory content with auto-detection
poetry run python manage.py create_smart_theory_lesson --lesson-id 5 --auto-title
```

### Splitting Large Vocabulary Lessons
```bash
# 1. Identify large vocabulary lessons to split
poetry run python manage.py split_vocabulary_lesson --scan-all

# 2. Preview splitting for a specific lesson
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --dry-run --interactive

# 3. Split lesson with manual word selection
poetry run python manage.py split_vocabulary_lesson --lesson-id=151 --parts=3 --target-units=15,22 --interactive --manual-selection

# 4. Create matching exercises for the new lessons
poetry run python manage.py matching_commands create --lesson-id=15
poetry run python manage.py matching_commands create --lesson-id=<new_lesson_id>
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

### Creating Theory Content
```bash
# 1. Check what's missing
poetry run python manage.py analyze_missing_theory

# 2. Preview creation for specific lesson
poetry run python manage.py create_smart_theory_lesson --lesson-id 162 --auto-title --dry-run

# 3. Create theory content
poetry run python manage.py create_smart_theory_lesson --lesson-id 162 --auto-title

# 4. Or create for all missing lessons
poetry run python manage.py analyze_missing_theory --create
```

## Theory Content Details

### Available Templates
The `create_smart_theory_lesson` command includes templates for common topics:
- `articles` - Definite/indefinite articles (the, a, an, le, la, un, une)
- `dates` - Dates and calendar vocabulary
- `time` - Time-related vocabulary
- `numbers` - Numbers and counting
- `colors` - Color vocabulary
- `family` - Family member terms
- `greetings` - Common greetings
- `pronouns` - Personal pronouns
- `verbs` - Verb conjugations
- `generic` - Default template for other topics

Templates are automatically selected based on lesson title keywords. You can also specify a template manually.

### Title Detection
The smart title extraction looks for patterns in lesson titles:
- "Unit X - Topic - Type" → "Topic"
- "Topic - Type" → "Topic"  
- Falls back to first part before any delimiter

Examples:
- "Unit 3 - Articles - Grammar" → "Articles"
- "Dates and Time - Vocabulary" → "Dates and Time"
- "Greeting - Vocabulary" → "Greeting"

## Getting Help

To see available subcommands and options:
```bash
poetry run python manage.py matching_commands --help
poetry run python manage.py testrecap_commands --help
poetry run python manage.py course_maintenance --help
poetry run python manage.py split_vocabulary_lesson --help
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


### Theory Content Analysis Scripts

Additional utility scripts for theory content management are now located in `scripts/course/theory/`:

```bash
# 1. Verify and fix duplicate theories
python scripts/course/theory/find_duplicate_theories.py

# 2. Intelligent duplicate removal (keeps best version)
python scripts/course/theory/fix_duplicate_theories_smart.py

# 3. Detailed inspection of duplicates
python scripts/course/theory/inspect_duplicate_theories.py

# 4. Debug theory creation issues
python scripts/course/theory/debug_theory_creation.py

# 5. Complete theory content report
python scripts/course/theory/theory_content_report.py

# 6. Fix theory content_type case issues
python scripts/course/theory/fix_theory_case.py

# 7. Preview theory creation for specific lessons
python scripts/course/theory/preview_theory_creation.py --lesson-id 12
```

### Matching Exercise Scripts

Utility scripts for matching exercises are located in `scripts/course/matching/`:

```bash
# Debug matching exercises
python scripts/course/matching/debug_matching_exercises.py

# List matching issues
python scripts/course/matching/list_matching_issues.py

# Split matching exercises
python scripts/course/matching/split_matching_exercises.py

# Update matching pairs count
python scripts/course/matching/update_matching_pairs_count.py
```

### Quick Diagnostics

```bash
# Check overall theory coverage
python manage.py analyze_missing_theory --report

# Find duplicate theories
python manage.py analyze_missing_theory --check-duplicates

# Debug specific lessons
python scripts/course/theory/inspect_duplicate_theories.py

# Full system diagnostic
python scripts/course/theory/theory_content_report.py
```

## Project Structure

The commands are organized as follows:

```
backend/apps/course/management/commands/
├── README.md
├── analyze_missing_theory.py        # Main theory analysis command
├── create_smart_theory_lesson.py    # Main theory creation command
├── matching_commands.py             # Main matching exercises command
├── testrecap_commands.py           # Main test recap command
├── course_maintenance.py           # Main maintenance command
├── speaking_auto_associate.py      # Main speaking exercises command
└── split_vocabulary_lesson.py      # Main vocabulary splitting command

backend/scripts/course/
├── theory/                         # Theory-related utility scripts
│   ├── debug_theory_creation.py
│   ├── find_duplicate_theories.py
│   └── ... (other theory utilities)
├── matching/                       # Matching exercise utilities
│   ├── debug_matching_exercises.py
│   ├── list_matching_issues.py
│   └── ... (other matching utilities)
└── utilities/                      # General utilities
    └── remove_default_content_lesson.py
```
---

Last updated: 2025-05-20
Version: 2.4 (Added vocabulary splitting command)