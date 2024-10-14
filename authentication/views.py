# authentication/views.py
from django.conf import settings
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin

from .forms import SignupForm, StudentProfileForm, TeacherProfileForm, UploadStudentProfilePhotoForm, UploadTeacherProfilePhotoForm, TeacherRegistrationForm
from .models import StudentProfile, TeacherProfile

def choose_user_type(request):
    return render(request, 'authentication/choose_user_type.html')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        student_form = StudentProfileForm(request.POST)
        teacher_form = TeacherProfileForm(request.POST)
        
        if form.is_valid():
            user = form.save(commit=False)
            user_type = form.cleaned_data.get('user_type')
            
            if user_type == 'student':
                if student_form.is_valid():
                    user.is_student = True
                    user.save()
                    student_profile = student_form.save(commit=False)
                    student_profile.user = user
                    student_profile.save()
                    login(request, user)
                    messages.success(request, "Your account has been created successfully.")
                    return redirect(settings.LOGIN_REDIRECT_URL)
            elif user_type == 'teacher':
                if teacher_form.is_valid():
                    user.is_teacher = True
                    user.save()
                    teacher_profile = teacher_form.save(commit=False)
                    teacher_profile.user = user
                    teacher_profile.save()
                    login(request, user)
                    messages.success(request, "Your account has been created successfully.")
                    return redirect('teacher_dashboard')
    else:
        form = SignupForm()
        student_form = StudentProfileForm()
        teacher_form = TeacherProfileForm()

    return render(request, 'authentication/signup.html', {
        'form': form,
        'student_form': student_form,
        'teacher_form': teacher_form
    })

@login_required
def student_dashboard(request):
    return render(request, 'authentication/student_dashboard.html')

@login_required
def teacher_dashboard(request):
    return render(request, 'authentication/teacher_dashboard.html')

class UploadProfilePhotoView(LoginRequiredMixin, View):
    @login_required
    def get(self, request):
        if request.user.is_student:
            profile = StudentProfile.objects.get(user=request.user)
            form = UploadStudentProfilePhotoForm(instance=profile)
        elif request.user.is_teacher:
            profile = TeacherProfile.objects.get(user=request.user)
            form = UploadTeacherProfilePhotoForm(instance=profile)
        else:
            form = None  # Handle case where user is neither student nor teacher

        return render(request, 'authentication/upload_profile_photo.html', context={'form': form})

    @login_required
    def post(self, request):
        if request.user.is_student:
            profile = StudentProfile.objects.get(user=request.user)
            form = UploadStudentProfilePhotoForm(request.POST, request.FILES, instance=profile)
        elif request.user.is_teacher:
            profile = TeacherProfile.objects.get(user=request.user)
            form = UploadTeacherProfilePhotoForm(request.POST, request.FILES, instance=profile)
        else:
            form = None  # Handle case where user is neither student nor teacher

        if form and form.is_valid():
            form.save()
            messages.success(request, 'Profile picture uploaded successfully')
            return redirect('index')

        return render(request, 'authentication/upload_profile_photo.html', context={'form': form})

@login_required
def delete_account(request):
    if request.method == 'POST':
        if request.POST.get('confirm_delete'):
            request.user.delete()
            messages.success(request, "Votre compte a été supprimé avec succès.")
            return redirect('index')
        else:
            messages.error(request, "La suppression du compte a été annulée.")
            return redirect('index')
    else:
        return render(request, 'authentication/confirm_delete_account.html')

def register_teacher(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('teacher_dashboard')  # Redirect to the teacher dashboard
    else:
        form = TeacherRegistrationForm()

    return render(request, 'authentication/register_teacher.html', {'form': form})
