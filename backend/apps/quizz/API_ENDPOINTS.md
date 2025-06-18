# Quiz App API Endpoints

This document lists all available API endpoints for the quiz application.

## Base URL
All endpoints are prefixed with: `/api/v1/quizz/`

## Main Quiz Endpoints (ViewSet)
- `GET /` - List all quizzes
- `POST /` - Create a new quiz
- `GET /{id}/` - Get specific quiz details
- `PUT /{id}/` - Update a quiz
- `DELETE /{id}/` - Delete a quiz
- `POST /{id}/start/` - Start a quiz session
- `POST /{id}/submit/` - Submit quiz answers

## Analytics Endpoints
- `GET /analytics/stats/?timeframe={7d|30d|90d}` - Get user statistics
  - Returns: total quizzes, average score, time spent, streak, best/worst categories
- `GET /analytics/categories/?timeframe={7d|30d|90d}` - Get category performance
  - Returns: performance breakdown by quiz category
- `GET /analytics/timeline/?timeframe={7d|30d|90d}` - Get performance timeline
  - Returns: daily performance data for charts
- `GET /analytics/difficulty/?timeframe={7d|30d|90d}` - Get difficulty breakdown
  - Returns: performance by difficulty level

## Leaderboard Endpoints
- `GET /leaderboard/?category={all|category}&timeframe={weekly|monthly|all-time}&limit={number}` - Get leaderboard rankings
- `GET /leaderboard/my_rank/?category={all|category}&timeframe={weekly|monthly|all-time}` - Get current user's rank
- `GET /leaderboard/categories/` - Get available quiz categories for leaderboard filtering

## Achievements Endpoint
- `GET /achievements/` - Get user's achievement progress and unlocked achievements

## Authentication
All endpoints require authentication via session or token.

## Data Seeding
To create test data for development:
```bash
python manage.py seed_quiz_data --users 10 --quizzes 5
```

## Frontend Integration
The frontend quiz application automatically uses these endpoints through:
- `src/addons/quizz/api/analyticsAPI.ts`
- `src/addons/quizz/api/leaderboardAPI.ts`
- `src/addons/quizz/hooks/useQuizApi.ts`

All API calls include automatic retry logic and error handling.