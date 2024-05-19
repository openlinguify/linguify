# authentication views
from django.conf import settings
from django.contrib.auth import login, logout
from django.shortcuts import render, redirect
from django.views.generic import View
from django.views import View
from . import forms


def signup_page(request):
    form = forms.SignupForm()
    if request.method == 'POST':
        form = forms.SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            # auto-login user
            login(request, user)
            return redirect(settings.LOGIN_REDIRECT_URL)
    return render(request, 'authentication/signup.html', context={'form': form})


class UploadProfilePhotoView(View):
    def get(self, request):
        form = forms.UploadProfilePhotoForm(instance=request.user)
        return render(request, 'authentication/upload_profile_photo.html', context={'form': form})

    def post(self, request):
        form = forms.UploadProfilePhotoForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('index')
        return render(request, 'authentication/upload_profile_photo.html', context={'form': form})
        
