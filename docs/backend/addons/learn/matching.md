# Complete Guide to Matching Exercises

## Overview

The Linguify platform provides comprehensive tools to automate the creation, association, and management of matching exercises with vocabulary content. This guide covers everything from creating basic matching exercises to handling complex vocabulary splitting scenarios.

## Table of Contents
1. [Installation](#installation)
2. [Quick Start](#quick-start)
3. [Commands Overview](#commands-overview)
4. [Vocabulary Splitting](#vocabulary-splitting)
5. [Admin Interface](#admin-interface)
6. [Troubleshooting](#troubleshooting)
7. [Best Practices](#best-practices)
8. [Technical Details](#technical-details)

## Installation

The tools are installed as Django management commands in the folder:
```
backend/apps/course/management/commands/
```

Available commands:
- `matching_commands.py` - Unified command for create, associate, and fix operations
- `debug_matching_exercises.py` - Debug and inspect matching exercises
- `update_pairs_count.py` - Update pairs count to match actual vocabulary

The `__init__.py` files must exist in the `management/` and `management/commands/` folders for Django to recognize the commands.

## Quick Start

### Complete Automation (Recommended)

To automatically create matching exercises for all lessons with vocabulary:

```bash
# Create matching exercises for all lessons
poetry run python manage.py matching_commands create

# Create with vocabulary splitting (for large vocabulary lists)
poetry run python manage.py matching_commands create --split --pairs-per-exercise 5
```

### Single Lesson

```bash
# Create for a specific lesson
poetry run python manage.py matching_commands create --lesson-id 1
```

## Commands Overview

### 1. Unified Matching Commands

The `matching_commands` command supports three subcommands: `create`, `associate`, and `fix`.

#### Create and Associate

```bash
poetry run python manage.py matching_commands create [options]
```

Options:
- `--dry-run` - Preview what would be done without making changes
- `--force` - Force update even if associations exist
- `--lesson-id [ID]` - Process only a specific lesson
- `--pairs [N]` - Number of pairs per exercise (default: 8)
- `--split` - Split large vocabulary lists into multiple exercises
- `--pairs-per-exercise [N]` - When splitting, pairs per exercise (default: 5)

Examples:
```bash
# Preview changes
poetry run python manage.py matching_commands create --dry-run

# Create with 10 pairs per exercise
poetry run python manage.py matching_commands create --pairs 10

# Split 16 vocabulary items into exercises with 5 pairs each
poetry run python manage.py matching_commands create --split --pairs-per-exercise 5 --lesson-id 1
```

#### Associate Vocabulary

```bash
poetry run python manage.py matching_commands associate [options]
```

Options:
- `--lesson [ID]` - Process only the specified content lesson ID
- `--force` - Replace existing associations
- `--debug` - Show debug information

#### Fix Associations

```bash
poetry run python manage.py matching_commands fix [options]
```

Options:
- `--lesson-id [ID]` - Process only a specific lesson
- `--force` - Force update even if associations exist
- `--verbose` - Show detailed output

### 2. Debug Commands

```bash
poetry run python manage.py debug_matching_exercises [options]
```

Options:
- `--lesson-id [ID]` - Debug specific lesson
- `--exercise-id [ID]` - Debug specific exercise

Examples:
```bash
# Debug specific lesson
poetry run python manage.py debug_matching_exercises --lesson-id 1

# Show summary of all exercises
poetry run python manage.py debug_matching_exercises
```

### 3. Update Pairs Count

```bash
poetry run python manage.py update_pairs_count [options]
```

Options:
- `--exercise-id [ID]` - Update specific exercise
- `--lesson-id [ID]` - Update all exercises in a lesson
- `--fix-all` - Fix all mismatched exercises
- `--dry-run` - Preview changes

Examples:
```bash
# Fix specific exercise
poetry run python manage.py update_pairs_count --exercise-id 1

# Preview all fixes
poetry run python manage.py update_pairs_count --fix-all --dry-run
```

## Vocabulary Splitting

### Problem

When a lesson has a large vocabulary list (e.g., 16 items), the default matching exercise only displays 8 pairs due to the `pairs_count` limit.

### Solution

Use the `--split` option to create multiple smaller exercises:

```bash
# Split 16 vocabulary items into multiple exercises
poetry run python manage.py matching_commands create --split --pairs-per-exercise 5 --lesson-id 1
```

This creates:
- Exercise 1: 5 pairs
- Exercise 2: 5 pairs
- Exercise 3: 5 pairs
- Exercise 4: 1 pair

### Examples

```bash
# Without split (default): 1 exercise with 8 pairs
poetry run python manage.py matching_commands create --lesson-id 1

# Split into 4 exercises with 4 pairs each
poetry run python manage.py matching_commands create --split --pairs-per-exercise 4 --lesson-id 1

# Split into 2 exercises with 8 pairs each
poetry run python manage.py matching_commands create --split --pairs-per-exercise 8 --lesson-id 1
```

## Admin Interface

### Django Admin Features

The admin interface shows:
- `pairs_count`: The configured number of pairs
- `Vocab réel`: The actual number of vocabulary items (shown in red if mismatched)

### Admin Actions

1. Access the admin interface at `/admin/course/matchingexercise/`
2. Select the exercises to update
3. In the "Actions" dropdown menu, choose "Associate vocabulary items from lessons"
4. Click "Go"

## Troubleshooting

### Common Issues

| Problem | Solution |
|----------|----------|
| "Still shows 8 pairs" | Update pairs_count: `poetry run python manage.py update_pairs_count --exercise-id 1` |
| "No vocabulary items found" | Verify vocabulary exists in content lessons with type containing "vocabulary" |
| No exercises created | Check content_type is set correctly (should contain "vocabularylist") |
| API returns wrong data | Ensure exercise has correct `pairs_count` value |
| Database errors | Run with `--fix-sequence` to fix ID sequences |

### Debug Process

1. Check current state:
   ```bash
   poetry run python manage.py debug_matching_exercises --lesson-id 1
   ```

2. Update pairs count if needed:
   ```bash
   poetry run python manage.py update_pairs_count --lesson-id 1
   ```

3. Fix associations if needed:
   ```bash
   poetry run python manage.py matching_commands fix --lesson-id 1
   ```

## Best Practices

### For New Content

1. Create lessons with vocabulary content first
2. Use `create` with `--split` for large vocabulary lists
3. Verify with `debug_matching_exercises`

### For Existing Content

1. Diagnose issues: `debug_matching_exercises`
2. Fix pairs count: `update_pairs_count`
3. Fix associations: `matching_commands fix`

### Optimal Exercise Sizes

- **Standard size**: 5-8 pairs per exercise
- **For memorization**: 4-6 pairs
- **For review**: 8-10 pairs
- **Large lists**: Split into multiple exercises

### Command Workflow

```bash
# 1. Preview what will be done
poetry run python manage.py matching_commands create --dry-run --lesson-id 1

# 2. Create with appropriate splitting
poetry run python manage.py matching_commands create --split --pairs-per-exercise 5 --lesson-id 1

# 3. Verify the result
poetry run python manage.py debug_matching_exercises --lesson-id 1

# 4. Fix any issues
poetry run python manage.py update_pairs_count --lesson-id 1
```

## Technical Details

### Database Schema

The `MatchingExercise` model has:
- `pairs_count`: PositiveIntegerField (default: 8, min: 4, max: 20)
- `vocabulary_words`: ManyToManyField to VocabularyList

### Content Type Matching

The system looks for content lessons with `content_type` containing:
- "vocabulary"
- "vocabularylist" 
- "VocabularyList"
- "matching"

The search is case-insensitive.

### Association Process

For each matching exercise, the association process:
1. Checks if vocabulary associations already exist
2. Searches for vocabulary in this order:
   - Same content lesson (if it's a vocabulary type)
   - Other vocabulary content lessons in the same parent lesson
3. Associates vocabulary up to the `pairs_count` limit
4. Randomly orders vocabulary for variation

### Frontend Integration

The frontend displays:
- Actual number of pairs from `target_words.length`
- Progress as "X/Y matched" where Y is the actual pairs count
- Dynamic updating based on API data

### API Response

The API returns:
```json
{
  "exercise_data": {
    "target_words": ["word1", "word2", ...],
    "native_words": ["mot1", "mot2", ...],
    "correct_pairs": {
      "word1": "mot1",
      "word2": "mot2"
    }
  },
  "pairs_count": 5
}
```

### Performance Considerations

- Vocabulary queries are optimized with proper indexing
- Batch operations minimize database calls
- The system handles large vocabulary sets efficiently
- Split operations create exercises sequentially to maintain order

### Error Handling

- All commands include comprehensive error handling
- Detailed error messages help diagnose issues
- Dry-run mode allows safe testing
- Database transactions ensure consistency

---

*Last updated: 2025 - Version 3.0*