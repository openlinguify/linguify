# teaching/views.py
from django.shortcuts import render

def teaching(request):
    return render(request, 'teaching/teaching_dashboard.html')