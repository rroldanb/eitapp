from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
# from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from apps.usuarios.forms import TaskForm
from apps.tasks.models.tasks import Task

@login_required
def tasks(request):
   tasks = Task.objects.filter(user=request.user, is_completed=False)
#   tasks = Task.objects.all()
   return render(request, 'tasks.html', {'tasks': tasks, 'list_title': 'Pending Tasks'})

@login_required
def tasks_completed(request):
   tasks = Task.objects.filter(user=request.user, is_completed=True).order_by('-date_completed')
   return render(request, 'tasks.html', {'tasks': tasks, 'list_title': 'Completed Tasks'})

@login_required
def task_detail(request, task_id):
    #task = Task.objects.get(id=task_id)
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'GET':
        # task = get_object_or_404(Task, id=task_id)
        form = TaskForm(instance=task)
        return render(request, 'task_detail.html', {'task': task, 'form': form})
    else:
        try:
            form = TaskForm(request.POST, instance=task)
            if form.is_valid():
                form.save()
                return redirect('tasks')
        except Exception as e:
            return render(request, 'task_detail.html', {'task': task, 'form': form, 'error': str(e)})

@login_required
def create_task(request):
    #return render(request, 'create_task.html')
   if request.method == 'GET':
       return render(request, 'create_task.html', {
           'form': TaskForm
       })
   else:
       try:
           form = TaskForm(request.POST)
           #if form.is_valid():
           new_task = form.save(commit=False)
           new_task.user = request.user
           new_task.save()
           return redirect('tasks')
       except Exception as e:
           return render(request, 'create_task.html', {
               'form': form,
               'error': str(e)
           })

@login_required
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.is_completed = True
        task.date_completed = timezone.now()
        task.save()
        return redirect('tasks')

@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    task.delete()
    return redirect('tasks')
