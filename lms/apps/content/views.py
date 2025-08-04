from django.shortcuts import render
from django.http import HttpResponse

def content_list(request):
    """List view for content"""
    return render(request, 'content/list.html')
