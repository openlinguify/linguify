from django.shortcuts import render

# Create your views here.
def student_dashboard(request):
    return render(request, 'teaching/student_dashboard.html')

def teacher_dashboard(request):
    return render(request, 'teaching/teacher_dashboard.html')

def teacher_profile(request):
    return render(request, 'teaching/teacher_profile.html')

def student_profile(request):
    return render(request, 'teaching/student_profile.html')
