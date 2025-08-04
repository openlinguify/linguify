from django.shortcuts import render
from django.http import HttpResponse

def analytics_list(request):
    """List view for analytics"""
    return render(request, 'analytics/list.html')
