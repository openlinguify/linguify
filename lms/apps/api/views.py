from django.shortcuts import render
from django.http import HttpResponse

def api_list(request):
    """List view for api"""
    return render(request, 'api/list.html')
