from django.shortcuts import render
from django.http import HttpResponse

def assessments_list(request):
    """List view for assessments"""
    return render(request, 'assessments/list.html')
