from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils import timezone
from apps.tasks.models.tasks import Task, TaskStatus
from apps.tasks.forms import TaskForm, BulkTaskForm
from apps.usuarios.models import Role
from apps.usuarios.utils import get_user_role


@login_required
def task_list(request):
    role = get_user_role(request.user)
    status_filter = request.GET.get('status', '')

    if role >= Role.ADMIN:
        tasks = Task.objects.all()
    elif role >= Role.MODELADOR:
        tasks = Task.objects.filter(created_by=request.user)
    else:
        tasks = Task.objects.filter(assignee=request.user)

    if status_filter:
        tasks = tasks.filter(status=status_filter)

    tasks = tasks.select_related('assignee', 'created_by', 'proyecto').order_by('-created_at')
    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'current_status': status_filter,
    })


@login_required
def task_detail(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    role = get_user_role(request.user)

    if role < Role.MODELADOR and task.assignee != request.user:
        messages.error(request, 'No tienes permiso para ver esta tarea.')
        return redirect('task_list')

    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Tarea actualizada.')
            return redirect('task_list')
        return render(request, 'tasks/task_detail.html', {'task': task, 'form': form})
    else:
        form = TaskForm(instance=task, user=request.user)
        return render(request, 'tasks/task_detail.html', {'task': task, 'form': form})


@login_required
def create_task(request):
    role = get_user_role(request.user)
    if role < Role.MODELADOR:
        messages.error(request, 'No tienes permiso para crear tareas.')
        return redirect('task_list')

    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            messages.success(request, 'Tarea creada.')
            return redirect('task_list')
        return render(request, 'tasks/create_task.html', {'form': form})
    else:
        form = TaskForm(user=request.user)
        return render(request, 'tasks/create_task.html', {'form': form})


@login_required
def bulk_create_tasks(request):
    role = get_user_role(request.user)
    if role < Role.ADMIN:
        messages.error(request, 'Solo administradores pueden crear tareas masivas.')
        return redirect('task_list')

    if request.method == 'POST':
        form = BulkTaskForm(request.POST, user=request.user)
        if form.is_valid():
            titles = [t.strip() for t in form.cleaned_data['titles'].split('\n') if t.strip()]
            assignee = form.cleaned_data.get('assignee')
            proyecto = form.cleaned_data.get('proyecto')
            due_date = form.cleaned_data.get('due_date')
            for title in titles:
                Task.objects.create(
                    title=title,
                    created_by=request.user,
                    assignee=assignee,
                    proyecto=proyecto,
                    due_date=due_date,
                )
            messages.success(request, f'{len(titles)} tareas creadas.')
            return redirect('task_list')
        return render(request, 'tasks/bulk_create.html', {'form': form})
    else:
        form = BulkTaskForm(user=request.user)
        return render(request, 'tasks/bulk_create.html', {'form': form})


@login_required
@require_POST
def complete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    role = get_user_role(request.user)
    if role < Role.MODELADOR and task.assignee != request.user:
        messages.error(request, 'No tienes permiso para completar esta tarea.')
        return redirect('task_list')
    task.status = TaskStatus.COMPLETADA
    task.date_completed = timezone.now()
    task.save()
    messages.success(request, 'Tarea completada.')
    return redirect('task_list')


@login_required
@require_POST
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id)
    role = get_user_role(request.user)
    if role < Role.MODELADOR and task.assignee != request.user:
        messages.error(request, 'No tienes permiso para eliminar esta tarea.')
        return redirect('task_list')
    task.delete()
    messages.success(request, 'Tarea eliminada.')
    return redirect('task_list')
