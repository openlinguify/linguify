from django.shortcuts import render
from django.http import HttpResponse

def institution_list(request):
    """List all institutions"""
    return render(request, 'institutions/list.html')

def institution_register(request):
    """Register a new institution"""
    return render(request, 'institutions/register.html')