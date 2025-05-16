# TestRecap API Integration

This document explains how TestRecap functionality is integrated between frontend and backend.

## Overview

The TestRecap feature allows users to take tests that review lesson content. The system needs to determine which TestRecap is associated with a given ContentLesson.

## Backend Implementation

The backend provides a dedicated endpoint to find the appropriate TestRecap for any ContentLesson:

```
GET /api/v1/course/test-recap/for-content-lesson/?content_lesson_id={id}
```

This endpoint implements multiple strategies to find the correct TestRecap:

1. First approach: Check if the content lesson itself is a TestRecap type and use its title to find a matching TestRecap
2. Second approach: Use the parent lesson to find an associated TestRecap
3. Third approach: Look for TestRecaps associated with sibling content lessons in the same lesson
4. Last resort: Return any TestRecap in the same unit or the first available TestRecap

## Frontend Implementation

The frontend uses the following approach to get the TestRecap:

1. Call the dedicated backend endpoint: `/api/v1/course/test-recap/for-content-lesson/`
2. If that fails, try the direct endpoint: `/api/v1/course/content-lesson/{id}/test-recap/`
3. If all attempts fail, display demo content

## Usage Guidelines

When you need to find a TestRecap associated with a ContentLesson:

```typescript
// Preferred approach - use courseAPI
const testRecapId = await courseAPI.getTestRecapIdFromContentLesson(contentLessonId);

// Alternative approach - use testRecapAPI directly
const response = await testRecapAPI.getTestRecapForContentLesson(contentLessonId);
const testRecap = response.data;
```

## Benefits

This implementation provides:

1. **Reliability**: Multiple fallback strategies ensure users always see content
2. **Maintainability**: Business logic primarily in the backend
3. **Performance**: Reduced number of API calls (from potentially 3+ calls to 1-2)
4. **Consistency**: Standardized approach to finding TestRecaps