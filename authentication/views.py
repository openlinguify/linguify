# authentication views
from django.conf import settings
from django.contrib.auth import login
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views import View
from .forms import SignupForm, StudentProfileForm, TeacherProfileForm, UploadStudentProfilePhotoForm, UploadTeacherProfilePhotoForm
from .models import StudentProfile, TeacherProfile

def choose_user_type(request):
    return render(request, 'authentication/choose_user_type.html')

def signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            if user.user_type == 'student':
                student_form = StudentProfileForm(request.POST, instance=user.student_profile)
                if student_form.is_valid():
                    user.is_student = True
                    user.save()
                    student_form.save()
                    login(request, user)
                    messages.success(request, "Your account has been created successfully.")
                    return redirect(settings.LOGIN_REDIRECT_URL)
            elif user.user_type == 'teacher':
                teacher_form = TeacherProfileForm(request.POST, instance=user.teacher_profile)
                if teacher_form.is_valid():
                    user.is_teacher = True
                    user.save()
                    teacher_form.save()
                    login(request, user)
                    messages.success(request, "Your account has been created successfully.")
                    return redirect('teacher_dashboard')
    else:
        form = SignupForm()
        student_form = StudentProfileForm()
        teacher_form = TeacherProfileForm()
    return render(request,
                  'authentication/signup.html',
                  {'form': form,
                   'student_form': student_form,
                   'teacher_form': teacher_form
  })


def student_dashboard(request):
    return render(request, 'authentication/student_dashboard.html')

def teacher_dashboard(request):
    return render(request, 'authentication/teacher_dashboard.html')


class UploadProfilePhotoView(View):
    def get(self, request):
        if request.user.user_type == 'student':
            profile = StudentProfile.objects.get(user=request.user)
            form = UploadStudentProfilePhotoForm(instance=profile)
        else:
            profile = TeacherProfile.objects.get(user=request.user)
            form = UploadTeacherProfilePhotoForm(instance=profile)

        return render(request, 'authentication/upload_profile_photo.html', context={'form': form})

    def post(self, request):
        if request.user.user_type == 'student':
            profile = StudentProfile.objects.get(user=request.user)
            form = UploadStudentProfilePhotoForm(request.POST, request.FILES, instance=profile)
        else:
            profile = TeacherProfile.objects.get(user=request.user)
            form = UploadTeacherProfilePhotoForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
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