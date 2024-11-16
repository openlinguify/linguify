# teaching/views.py
from django.shortcuts import render

def teaching(request):
    return render(request, '../../../frontend/public/templates_storage/teaching/teaching_dashboard.html')