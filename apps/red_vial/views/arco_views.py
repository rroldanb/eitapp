from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from apps.proyectos.models import Proyecto
from apps.red_vial.services.red_vial_service import *
from apps.red_vial.forms.arco_form import ArcoForm





# ========== ARCO VIEWS ==========

@login_required
def arcos_list_view(request, proyecto_id):
    """Vista de lista de arcos de un proyecto"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    arcos = get_arcos_by_proyecto(proyecto_id)
    return render(request, 'red_vial/arcos_list.html', {
        'proyecto': proyecto,
        'arcos': arcos
    })


@login_required
def arco_detail_view(request, arco_id):
    """Vista detalle de un arco"""
    arco = get_arco_by_id(arco_id)
    return render(request, 'red_vial/Arcos/arco_detail.html', {
        'arco': arco
    })


@login_required
def arco_create_view(request, proyecto_id):
    """Vista para crear un nuevo arco"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        form = ArcoForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            arco = form.save(commit=False)
            arco.proyecto = proyecto
            arco.save()
            return redirect('arcos_list', proyecto_id=proyecto_id)
    else:
        form = ArcoForm(proyecto=proyecto)

    return render(request, 'red_vial/arcos_list.html', {'proyecto': proyecto})


@login_required
def arco_update_view(request, arco_id):
    """Vista para actualizar un arco"""
    arco = get_arco_by_id(arco_id)

    if request.method == 'POST':
        form = ArcoForm(request.POST, instance=arco, proyecto=arco.proyecto)
        if form.is_valid():
            form.save()
            return redirect('arcos_list', proyecto_id=arco.proyecto.id)
    else:
        form = ArcoForm(instance=arco, proyecto=arco.proyecto)

    return render(request, 'red_vial/Arcos/arco_form.html', {
        'proyecto': arco.proyecto,
        'form': form,
        'arco': arco
    })


@login_required
def arco_delete_view(request, arco_id):
    """Vista para eliminar un arco"""
    arco = get_arco_by_id(arco_id)
    proyecto_id = arco.proyecto.id
    arco_delete(arco_id)
    return redirect('arcos_list', proyecto_id=proyecto_id)
