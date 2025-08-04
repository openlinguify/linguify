from django.shortcuts import render
from django.http import HttpResponse

def courses_list(request):
    """List view for courses"""
    return render(request, 'courses/list.html')
