from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm
from administrator.decorators import admin_required
from django.contrib.sessions.models import Session
from django.contrib.auth.models import Group
from administrator.models import ParentLogin, TeacherLogin


# Create your views here.

from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import *
from .forms import CreateUserForm


# def registerPage(request):
#     if request.user.is_authenticated:
#         return redirect('administrator')
#     else:
#         form = CreateUserForm()

#         if request.method == 'POST':
#             form = CreateUserForm(request.POST)
#             if form.is_valid():
#                 form.save()
#                 user = form.cleaned_data.get('username')
#                 messages.success(request, 'Account was created for ' + user)
#                 return redirect('login')
#         context = {
#             'form': form
#         }

#         return render(request, 'register.html', context)

def loginPage(request):
    error_message = None
    username = None
    first_name = None
    session_message = None  # Initialize session_message variable

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            if user.groups.filter(name='Parent').exists():
                ParentLogin.objects.create(parent=user)
            if user.groups.filter(name='Teacher').exists():
                TeacherLogin.objects.create(teacher=user)
            # Pass the username to the template
            return redirect('dashboard')
            # return render(request, 'master_admin.html', {'username': username, 'first_name' : first_name })
            
        else:
            error_message = 'Username OR password is incorrect.'

    # If the user is logged in, include the session message in the context
    if 'logged_in' in request.session and not request.session['logged_in']:
        session_message = 'Your session has expired. Please log in again.'
        request.session['logged_in'] = False

    return render(request, 'login.html', {'error_message': error_message, 'username': username, 'session_message': session_message, 'first_name' : first_name })




def logoutUser(request):
    # Check if user is logged in before logging out
    if request.session.get('logged_in'):
        # Clear session variables
        request.session.flush()
        messages.success(request, 'You have been logged out. Your session has expired.')
    # else:
    #     messages.info(request, 'You are not logged in.')

    logout(request)
    return redirect('login')
