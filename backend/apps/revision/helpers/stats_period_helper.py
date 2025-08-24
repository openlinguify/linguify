from datetime import datetime, timedelta
from django.utils import timezone


class StatsPeriodHelper:
    """Helper class to handle statistics period calculations."""
    
    VALID_PERIODS = ['week', 'month', 'year', 'lifetime']
    
    def __init__(self, period='week'):
        if period not in self.VALID_PERIODS:
            period = 'week'
        self.period = period
    
    def get_date_range(self):
        """Get start and end dates for the period."""
        now = timezone.now()
        
        if self.period == 'week':
            start_date = now - timedelta(days=7)
        elif self.period == 'month':
            start_date = now - timedelta(days=30)
        elif self.period == 'year':
            start_date = now - timedelta(days=365)
        else:  # lifetime
            start_date = datetime(2020, 1, 1, tzinfo=timezone.utc)
        
        return start_date, now
    
    def get_period_label(self):
        """Get human-readable period label."""
        labels = {
            'week': 'Cette semaine',
            'month': 'Ce mois',
            'year': 'Cette année',
            'lifetime': 'Depuis le début'
        }
        return labels.get(self.period, 'Cette semaine')