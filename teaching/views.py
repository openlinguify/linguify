# teaching/views.py
from django.shortcuts import render

def teaching(request):
    return render(request, 'teaching_dashboard.html')