from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from apps.usuarios.forms import TaskForm
from apps.tasks.models.tasks import Task


def home(request):
    # return render(request, 'helloworld.html')
   #  return HttpResponse('<h1>Hello World</h1>')
   return render(request, 'home.html')

def signup(request):
   if request.method == 'GET':
    return render(request, 'signup.html', {
       'form': UserCreationForm
       })

   else:
       if request.POST['password1'] == request.POST['password2']:
           #register user
           try:
               user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
               user.save()
               login(request, user)
               return redirect('home')
            #    return HttpResponse('<h1>User created successfully</h1>')
           except IntegrityError:
            return render(request, 'signup.html', {
               'form': UserCreationForm,
               'error': 'Username already exists'
           })


       else:
           return render(request, 'signup.html', {
               'form': UserCreationForm,
               'error': 'Passwords do not match'
           })

def signin(request):

    if request.method == 'GET':
        return render(request, 'signin.html', {
            'form': AuthenticationForm
        })
    else:
        user = authenticate(request, username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            login(request, user)
            return redirect(request.GET.get('next', 'home'))
        else:
            return render(request, 'signin.html', {
                'form': AuthenticationForm,
                'error': 'Invalid username or password'
            })

@login_required
def signout(request):
    logout(request)
    return redirect('home')

