from django.shortcuts import render, redirect, get_object_or_404
from apps.proyectos.models import Proyecto
from django.contrib.auth.decorators import login_required
from apps.red_vial.services.red_vial_service import *
from apps.red_vial.forms.forms import  NodoForm

# ========== NODO VIEWS ==========

@login_required
def nodos_list_view(request, proyecto_id):
    """Vista de lista de nodos de un proyecto"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    nodos = get_nodos_by_proyecto(proyecto_id)
    return render(request, 'red_vial/Nodos/nodos_list.html', {
        'proyecto': proyecto,
        'nodos': nodos
    })


@login_required
def nodo_detail_view(request, nodo_id):
    """Vista detalle de un nodo"""
    nodo = get_nodo_by_id(nodo_id)
    arcos = get_arcos_by_nodo(nodo_id)
    return render(request, 'red_vial/nodo_detail.html', {
        'nodo': nodo,
        'arcos': arcos
    })

@login_required
def nodo_create_view(request, proyecto_id):
    """Vista para crear un nuevo nodo"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    if request.method == 'POST':
        form = NodoForm(request.POST, proyecto=proyecto)

        if form.is_valid():
            nodo = form.save(commit=False)
            nodo.proyecto = proyecto
            nodo.save()
            return redirect('proyecto_nodos', proyecto_id=proyecto_id)
    else:
        form = NodoForm(proyecto=proyecto)

    return render(request, 'Nodos/proyecto_nodos.html', {
        'proyecto': proyecto,
        'form': form
    })



@login_required
def nodo_update_view(request, nodo_id):
    """Vista para actualizar un nodo"""
    nodo = get_nodo_by_id(nodo_id)

    if request.method == 'POST':
        form = NodoForm(request.POST, instance=nodo, proyecto=nodo.proyecto)
        if form.is_valid():
            form.save()
            return redirect('proyecto_nodos', proyecto_id=nodo.proyecto.id)
    else:
        form = NodoForm(instance=nodo, proyecto=nodo.proyecto)

    return render(request, 'red_vial/nodo_form.html', {
        'proyecto': nodo.proyecto,
        'form': form,
        'nodo': nodo
    })


@login_required
def nodo_delete_view(request, nodo_id):
    """Vista para eliminar un nodo"""
    nodo = get_nodo_by_id(nodo_id)
    proyecto_id = nodo.proyecto.id
    nodo_delete(nodo_id)
    return redirect('nodos_list', proyecto_id=proyecto_id)

@login_required
def proyecto_nodos_view(request, proyecto_id):
    """Vista de Nodos del proyecto"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    nodos = proyecto.nodos.all().select_related('calle_1', 'calle_2')

    return render(request, 'proyecto_nodos.html', {
        'proyecto': proyecto,
        'nodos': nodos,
        'active_section': 'nodos'
    })

