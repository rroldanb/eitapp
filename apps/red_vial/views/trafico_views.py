from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from apps.proyectos.models import Proyecto

from apps.red_vial.forms.periodo_form import PeriodoForm
from apps.red_vial.services.trafico_service import (
    get_all_periodos,
    get_periodo_by_id,
    periodo_delete,
)


# ========== PERIODO VIEWS ==========

@login_required
def periodos_list_view(request):
    """Vista de lista de períodos"""
    periodos = get_all_periodos()
    return render(request, 'red_vial/periodos_list.html', {
        'periodos': periodos
    })


@login_required
def periodo_create_view(request):
    """Vista para crear un nuevo período"""
    if request.method == 'POST':
        form = PeriodoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('periodos_list')
    else:
        form = PeriodoForm()

    return render(request, 'red_vial/periodo_form.html', {
        'form': form
    })


@login_required
def periodo_update_view(request, periodo_id):
    """Vista para actualizar un período"""
    periodo = get_periodo_by_id(periodo_id)

    if request.method == 'POST':
        form = PeriodoForm(request.POST, instance=periodo)
        if form.is_valid():
            form.save()
            return redirect('periodos_list')
    else:
        form = PeriodoForm(instance=periodo)

    return render(request, 'red_vial/periodo_form.html', {
        'form': form,
        'periodo': periodo
    })


@login_required
def periodo_delete_view(request, periodo_id):
    """Vista para eliminar un período"""
    periodo_delete(periodo_id)
    return redirect('periodos_list')
