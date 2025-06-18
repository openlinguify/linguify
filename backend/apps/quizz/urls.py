from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    QuizViewSet,
    AnalyticsStatsView,
    AnalyticsCategoriesView,
    AnalyticsTimelineView,
    AnalyticsDifficultyView
)
from .analytics_views import (
    LeaderboardView,
    LeaderboardMyRankView,
    LeaderboardCategoriesView,
    AchievementsView
)

router = DefaultRouter()
router.register(r'', QuizViewSet, basename='quiz')

app_name = 'quizz'

urlpatterns = [
    path('', include(router.urls)),
    
    # Analytics endpoints
    path('analytics/stats/', AnalyticsStatsView.as_view(), name='analytics-stats'),
    path('analytics/categories/', AnalyticsCategoriesView.as_view(), name='analytics-categories'),
    path('analytics/timeline/', AnalyticsTimelineView.as_view(), name='analytics-timeline'),
    path('analytics/difficulty/', AnalyticsDifficultyView.as_view(), name='analytics-difficulty'),
    
    # Leaderboard endpoints
    path('leaderboard/', LeaderboardView.as_view(), name='leaderboard'),
    path('leaderboard/my_rank/', LeaderboardMyRankView.as_view(), name='leaderboard-my-rank'),
    path('leaderboard/categories/', LeaderboardCategoriesView.as_view(), name='leaderboard-categories'),
    
    # Achievements endpoint
    path('achievements/', AchievementsView.as_view(), name='achievements'),
]