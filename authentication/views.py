# authentication views
from django.conf import settings
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.views.generic import View
from django.views import View
from . import forms
from .forms import SignupForm, UploadProfilePhotoForm


def signup_page(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, "Your account has been created successfully.")
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = SignupForm()
    return render(request, 'authentication/signup.html', {'form': form})


class UploadProfilePhotoView(View):
    @login_required
    def get(self, request):
        form = forms.UploadProfilePhotoForm(instance=request.user)
        return render(request, 'authentication/upload_profile_photo.html', context={'form': form})
    @login_required
    def post(self, request):
        form = forms.UploadProfilePhotoForm(request.POST, request.FILES, instance=request.user)
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
