from django.utils import timezone
from datetime import timedelta


def get_timeframe_filter(timeframe_param):
    """Helper function to get date filter based on timeframe"""
    now = timezone.now()
    
    if timeframe_param == '7d':
        return now - timedelta(days=7)
    elif timeframe_param == '30d':
        return now - timedelta(days=30)
    elif timeframe_param == '90d':
        return now - timedelta(days=90)
    elif timeframe_param == '1y':
        return now - timedelta(days=365)
    elif timeframe_param == 'weekly':
        return now - timedelta(days=7)
    elif timeframe_param == 'monthly':
        return now - timedelta(days=30)
    elif timeframe_param == 'all-time':
        return now - timedelta(days=3650)  # 10 years ago
    else:
        return now - timedelta(days=30)  # Default to 30 days