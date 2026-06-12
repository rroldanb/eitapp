from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from apps.usuarios.models import Role


def home(request):
   return render(request, 'home.html')

def signup(request):
   if request.method == 'GET':
    return render(request, 'signup.html', {
       'form': UserCreationForm
       })

   else:
       if request.POST['password1'] == request.POST['password2']:
           try:
               user = User.objects.create_user(username=request.POST['username'], password=request.POST['password1'])
               user.save()
               login(request, user)
               return redirect('home')
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
            request.session['show_pending_modal'] = True
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


from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import AdminUserCreationForm, SetPasswordForm
from django.contrib import messages
from django.views.decorators.http import require_POST


@staff_member_required
def admin_create_user_view(request):
    if request.method == 'POST':
        form = AdminUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            role_value = int(request.POST.get('role', Role.ENCUESTADOR))
            if hasattr(user, 'profile'):
                user.profile.role = role_value
                user.profile.save()
            messages.success(request, f'Usuario "{user.username}" creado con rol {Role(role_value).label}.')
            return redirect('user_management')
        return render(request, 'admin_create_user.html', {'form': form})
    return redirect('user_management')


@staff_member_required
def user_management_view(request):
    sort_map = {
        'username': 'username',
        'role': 'profile__role',
        'is_active': 'is_active',
    }
    sort_by = request.GET.get('sort_by', 'role')
    sort_order = request.GET.get('sort_order', 'desc')
    if sort_by not in sort_map:
        sort_by = 'role'
    if sort_order not in ('asc', 'desc'):
        sort_order = 'desc'

    order_prefix = '-' if sort_order == 'desc' else ''
    users = User.objects.all().select_related('profile').order_by(f'{order_prefix}{sort_map[sort_by]}', 'username')
    context = {'users': users, 'sort_by': sort_by, 'sort_order': sort_order}
    if request.headers.get('HX-Request'):
        return render(request, '_user_table.html', context)
    return render(request, 'user_management.html', context)


@staff_member_required
@require_POST
def user_toggle_active_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'No puedes deshabilitarte a ti mismo.')
    else:
        user.is_active = not user.is_active
        user.save()
        action = 'habilitado' if user.is_active else 'deshabilitado'
        messages.success(request, f'Usuario "{user.username}" {action}.')
    return redirect('user_management')


@staff_member_required
@require_POST
def user_change_role_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, 'No puedes cambiar tu propio rol.')
    else:
        new_role = int(request.POST.get('role', Role.ENCUESTADOR))
        if hasattr(user, 'profile'):
            user.profile.role = new_role
            user.profile.save()
        messages.success(request, f'Rol de "{user.username}" actualizado a {Role(new_role).label}.')
    return redirect('user_management')


@staff_member_required
def user_change_password_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = SetPasswordForm(user, request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, f'Contraseña de "{user.username}" actualizada.')
            return redirect('user_management')
    else:
        form = SetPasswordForm(user)
    return render(request, 'user_change_password.html', {'form': form, 'target_user': user})
