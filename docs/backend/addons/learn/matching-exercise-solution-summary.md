# Matching Exercises Complete Guide

## Overview

Matching exercises allow learners to associate vocabulary items from different languages. This guide covers the complete implementation, management, and optimization of matching exercises.

## Problem Identified and Solution

### Problem
Matching exercises were limited to showing only 8 pairs even when vocabulary lists contained more items (e.g., 16+ vocabulary items would still only show 8 pairs).

### Root Cause
The `MatchingExercise` model has a `pairs_count` field with a default value of 8, which wasn't being properly updated when exercises were created.

### Solution: Split Large Vocabulary Lists

⚠️ **Important**: If you have vocabulary lists with more than 8 items, you MUST use the split functionality to create multiple smaller exercises.

## Quick Start - Most Common Commands

```bash
# Create matching exercises for ONE lesson
poetry run python manage.py matching_commands create --lesson-id [LESSON_ID] --split --pairs-per-exercise 4

# Create matching exercises for ALL lessons at once
poetry run python manage.py create_all_matching_simple --pairs-per-exercise 4

# Check for issues
poetry run python manage.py list_matching_issues
```

## Complete Command Reference

### 1. Create Matching Exercises

#### For Single Lesson
```bash
# Basic creation
poetry run python manage.py matching_commands create --lesson-id [LESSON_ID]

# With splitting (RECOMMENDED for large vocab lists)
poetry run python manage.py matching_commands create --lesson-id [LESSON_ID] --split --pairs-per-exercise 4
```

#### For All Lessons
```bash
# Create for all lessons at once (RECOMMENDED)
poetry run python manage.py create_all_matching_simple --pairs-per-exercise 4

# Preview what will be created
poetry run python manage.py create_all_matching_simple --pairs-per-exercise 4 --dry-run

# Skip lessons that already have matching exercises
poetry run python manage.py create_all_matching_simple --pairs-per-exercise 4 --skip-existing
```

### 2. Update and Fix Exercises

```bash
# Update all exercises automatically
poetry run python manage.py update_all_matching_exercises --pairs-per-exercise 4

# Reset ALL matching exercises (delete and recreate)
poetry run python manage.py matching_commands reset --confirm --pairs-per-exercise 4

# Debug specific lesson
poetry run python manage.py debug_matching_exercises --lesson-id [LESSON_ID]
```

### 3. Diagnostic Commands

```bash
# List all matching exercises with issues
poetry run python manage.py list_matching_issues

# Debug vocabulary structure
poetry run python manage.py debug_vocabulary_structure

# Update pairs count to match actual vocabulary
poetry run python manage.py update_pairs_count
```

## Common Issues and Solutions

### Issue: Only 8 Pairs Showing

**Problem**: Despite having more vocabulary items, only 8 pairs are displayed.

**Solution**:
1. Delete the existing exercise (via Django admin)
2. Recreate with split:
```bash
poetry run python manage.py matching_commands create --lesson-id [LESSON_ID] --split --pairs-per-exercise 4
```

### Issue: No Matching Exercises Created

**Solution**: Create for all lessons at once:
```bash
poetry run python manage.py create_all_matching_simple --pairs-per-exercise 4
```

## Admin Interface Features

### Visual Indicators
- ✓ = Pairs count matches vocabulary count
- ⚠ = Pairs count lower than vocabulary (needs update)
- ↑ = Extra pairs (more than vocabulary)
- ❌ = No vocabulary associated

### Quick Actions
- **Split Large Exercises**: Automatically splits exercises with > 10 pairs
- **Optimize Pairs Count**: Updates pairs_count to match vocabulary
- **Check Consistency**: Verifies all exercises are properly configured

### Filters
- **Pairs Status**: Filter by indicator (Optimal, Needs Update, etc.)
- **Pairs Count Range**: Filter by number of pairs

## Frontend Display

The frontend automatically handles multiple exercises:
1. Shows exercise progression (e.g., "Exercise 1 of 4")
2. Provides navigation between exercises
3. Tracks completion for each sub-exercise
4. Only marks the lesson complete when all exercises are finished

## Best Practices

### 1. Optimal Configuration
- **Pairs per exercise**: 4-5 pairs (recommended)
- **Maximum pairs**: 8 (to avoid UI issues)
- **Minimum pairs**: 3 (for meaningful practice)

### 2. For Large Vocabulary Lists
- 10-20 items: 3-5 exercises of 4 pairs each
- 20-30 items: 5-7 exercises of 4 pairs each
- 30+ items: Consider breaking into themed groups

### 3. Regular Maintenance
```bash
# Weekly check for issues
poetry run python manage.py list_matching_issues

# Monthly optimization (dry run first)
poetry run python manage.py update_all_matching_exercises --dry-run
```

## Example Workflows

### Creating a New Lesson with Matching Exercise

1. Create the lesson and vocabulary content
2. Add vocabulary items (e.g., 17 vocabulary items)
3. Create matching exercises with split:
   ```bash
   poetry run python manage.py matching_commands create --lesson-id 123 --split --pairs-per-exercise 4
   ```
   This creates 5 exercises (4×4 pairs + 1×1 pair)

### Batch Creating for All Lessons

1. Check what will be created:
   ```bash
   poetry run python manage.py create_all_matching_simple --pairs-per-exercise 4 --dry-run
   ```

2. Execute creation:
   ```bash
   poetry run python manage.py create_all_matching_simple --pairs-per-exercise 4
   ```

3. Verify in admin interface

### Fixing Existing Issues

1. Identify problems:
   ```bash
   poetry run python manage.py list_matching_issues
   ```

2. Fix specific lesson:
   ```bash
   # Delete in admin, then:
   poetry run python manage.py matching_commands create --lesson-id [ID] --split --pairs-per-exercise 4
   ```

3. Or fix all at once:
   ```bash
   poetry run python manage.py update_all_matching_exercises --pairs-per-exercise 4
   ```

## Tested Example: Space & Astronomy Lesson

- **Before**: 25 vocabulary items, only 8 pairs showing
- **Command Used**: 
  ```bash
  poetry run python manage.py matching_commands create --lesson-id [ID] --split --pairs-per-exercise 5
  ```
- **After**: 5 exercises of 5 pairs each, all vocabulary accessible

## Summary

The key to successful matching exercises:

1. **Always use split functionality** for vocabulary lists > 8 items
2. **Use 4-5 pairs per exercise** for optimal learning
3. **Create for all lessons at once** using `create_all_matching_simple`
4. **Monitor regularly** using `list_matching_issues`
5. **Delete and recreate** when exercises show incorrect pair counts

Remember: The default pairs_count of 8 is a limitation, not a recommendation. Always split large vocabulary lists for optimal learning experience.