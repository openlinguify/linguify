from django.shortcuts import render
from django.http import HttpResponse

def instructors_list(request):
    """List view for instructors"""
    return render(request, 'instructors/list.html')
