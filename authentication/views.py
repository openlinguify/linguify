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


class LogoutView(View):
    def post(self, request):
        logout(request)
        return redirect(settings.LOGIN_REDIRECT_URL)


# class LoginPage(View):
#     form_class = forms.LoginView
#     templates_name = 'authentication/login.html'
#
#     def get(self, request):
#         form = self.form_class()
#         message = ''
#         return render(
#             request, self.templates_name, context={'form': form, 'message': message}
#         )
#
#     def post(self, request):
#         form = self.form_class(request.POST)
#         message = ''
#         if form.is_valid():
#             user = authenticate(
#                 username=form.cleaned_data['username'],
#                 password=form.cleaned_data['password']
#             )
#             if user is not None:
#                 login(request, user)
#                 return redirect('home')
#             else:
#                 message = 'Invalid username or password'
#         return render(
#             request, self.templates_name, context={'form': form, 'message': message}
#         )
#
#
# def logout_user(request):
#     logout(request)
#     return redirect('login')
#
#
# def login_page(request):
#     """
#     this function is used to allow the user to login
#     :param request:
#     :return:
#     """
#     form = forms.LoginForm()
#     message = ''
#     if request.method == 'POST':
#         form = forms.LoginForm(request.POST)
#         if form.is_valid():
#             user = authenticate(
#                 username=form.cleaned_data['username'],
#                 password=form.cleaned_data['password']
#             )
#             if user is not None:
#                 login(request, user)
#                 return redirect('home')
#             else:
#                 message = 'Invalid username or password'
#
#     return render(
#         request, 'authentication/login.html', context={'form': form, 'message': message}
#     )
