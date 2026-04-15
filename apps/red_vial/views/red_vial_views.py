from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.proyectos.models import Proyecto
from apps.red_vial.services.red_vial_service import *
from apps.red_vial.forms import (
    CalleForm,
    NodoForm,
    ArcoForm,
    RegulacionForm,
    NodoMovimientoForm,
    CoeficienteCruceForm,
)


# ========== CALLE VIEWS ==========

@login_required
def calles_list_view(request, proyecto_id):
    """Vista de lista de calles de un proyecto"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    calles = get_calles_by_proyecto(proyecto_id)
    return render(request, 'red_vial/calles_list.html', {
        'proyecto': proyecto,
        'calles': calles
    })


@login_required
def calle_detail_view(request, calle_id):
    """Vista detalle de una calle"""
    calle = get_calle_by_id(calle_id)
    # return redirect('calle_detail' , calle_id=calle_id)
    return render(request, 'red_vial/calle_detail.html', {
        'calle': calle,
        'calle_id': calle_id
    })


@login_required
def calle_create_view(request, proyecto_id):
    """Vista para crear una nueva calle"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'POST':
        form = CalleForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            calle = form.save(commit=False)
            calle.proyecto = proyecto
            calle.save()
            return redirect('proyecto_calles', proyecto_id=proyecto_id)
    else:
        form = CalleForm(proyecto=proyecto)

    return render(request, 'proyecto_calles.html', {
    'form': form,
    'proyecto': proyecto
})




@login_required
def calle_update_view(request, calle_id):
    """Vista para actualizar una calle"""
    calle = get_calle_by_id(calle_id)

    if request.method == 'POST':
        form = CalleForm(request.POST, instance=calle)
        if form.is_valid():
            form.save()
            return redirect('proyecto_calles', proyecto_id=calle.proyecto.id)
    else:
        form = CalleForm(instance=calle)

    return render(request, 'red_vial/calle_form.html', {
        'proyecto': calle.proyecto,
        'form': form,
        'calle': calle
    })


@login_required
def calle_delete_view(request, calle_id):
    """Vista para eliminar una calle"""
    calle = get_calle_by_id(calle_id)
    proyecto_id = calle.proyecto.id
    calle_delete(calle_id)
    return redirect('proyecto_calles', proyecto_id=proyecto_id)


# ========== NODO VIEWS ==========

@login_required
def nodos_list_view(request, proyecto_id):
    """Vista de lista de nodos de un proyecto"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    nodos = get_nodos_by_proyecto(proyecto_id)
    return render(request, 'red_vial/nodos_list.html', {
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

    return render(request, 'proyecto_nodos.html', {
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
    return redirect('proyecto_nodos', proyecto_id=proyecto_id)


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
    return render(request, 'red_vial/arco_detail.html', {
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
            return redirect('proyecto_arcos', proyecto_id=proyecto_id)
    else:
        form = ArcoForm(proyecto=proyecto)

    return render(request, 'proyecto_arcos.html', proyecto_id=proyecto.id)


@login_required
def arco_update_view(request, arco_id):
    """Vista para actualizar un arco"""
    arco = get_arco_by_id(arco_id)

    if request.method == 'POST':
        form = ArcoForm(request.POST, instance=arco, proyecto=arco.proyecto)
        if form.is_valid():
            form.save()
            return redirect('proyecto_arcos', proyecto_id=arco.proyecto.id)
    else:
        form = ArcoForm(instance=arco, proyecto=arco.proyecto)

    return render(request, 'red_vial/arco_form.html', {
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
    return redirect('proyecto_arcos', proyecto_id=proyecto_id)


# ========== REGULACIONES VIEWS ==========

@login_required
def regulaciones_list_view(request):
    """Vista de lista de tipos de regulación"""
    regulaciones = get_all_regulaciones()
    return render(request, 'red_vial/regulaciones_list.html', {
        'regulaciones': regulaciones
    })


@login_required
def regulacion_create_view(request):
    """Vista para crear un nuevo tipo de regulación"""
    if request.method == 'POST':
        form = RegulacionForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('regulaciones_list')
    else:
        form = RegulacionForm()

    return render(request, 'red_vial/regulacion_form.html', {
        'form': form
    })


# ========== NODO MOVIMIENTO VIEWS ==========

@login_required
def nodos_movimientos_list_view(request, proyecto_id):
    """Vista de lista de configuraciones nodo-movimiento"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    nodos_movimientos = get_nodos_movimientos_by_proyecto(proyecto_id)
    return render(request, 'red_vial/nodos_movimientos_list.html', {
        'proyecto': proyecto,
        'nodos_movimientos': nodos_movimientos
    })


@login_required
def nodo_movimiento_create_view(request, proyecto_id):
    """Vista para crear configuración nodo-movimiento"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    if request.method == 'POST':
        form = NodoMovimientoForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            nodo_mov = form.save(commit=False)
            nodo_mov.proyecto = proyecto
            nodo_mov.save()
            return redirect('nodos_movimientos_list', proyecto_id=proyecto_id)
    else:
        form = NodoMovimientoForm(proyecto=proyecto)

    return render(request, 'red_vial/nodo_movimiento_form.html', {
        'proyecto': proyecto,
        'form': form
    })


# ========== COEFICIENTE CRUCE VIEWS ==========

@login_required
def coeficientes_list_view(request):
    """Vista de lista de coeficientes de cruce"""
    coeficientes = get_all_coeficientes()
    return render(request, 'red_vial/coeficientes_list.html', {
        'coeficientes': coeficientes
    })


@login_required
def coeficiente_create_view(request):
    """Vista para crear un nuevo coeficiente"""
    if request.method == 'POST':
        form = CoeficienteCruceForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('coeficientes_list')
    else:
        form = CoeficienteCruceForm()

    return render(request, 'red_vial/coeficiente_form.html', {
        'form': form
    })


# ========== API VIEWS (JSON) ==========

@login_required
def api_calles_by_proyecto(request, proyecto_id):
    """API endpoint para obtener calles de un proyecto"""
    calles = get_calles_by_proyecto(proyecto_id)
    data = [{
        'id': str(c.id),
        'nombre': c.nombre,
        'numero': c.numero
    } for c in calles]
    return JsonResponse({'calles': data})


@login_required
def api_nodos_by_proyecto(request, proyecto_id):
    """API endpoint para obtener nodos de un proyecto"""
    nodos = get_nodos_by_proyecto(proyecto_id)
    data = [{
        'id': str(n.id),
        'numero': n.numero,
        'interseccion': n.interseccion
    } for n in nodos]
    return JsonResponse({'nodos': data})


@login_required
def api_arcos_by_proyecto(request, proyecto_id):
    """API endpoint para obtener arcos de un proyecto"""
    arcos = get_arcos_by_proyecto(proyecto_id)
    data = [{
        'id': str(a.id),
        'nodo_origen': a.nodo_origen.numero,
        'nodo_destino': a.nodo_destino.numero,
        'longitud': a.longitud
    } for a in arcos]
    return JsonResponse({'arcos': data})
