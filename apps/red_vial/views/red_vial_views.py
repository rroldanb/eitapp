from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from apps.proyectos.models import Proyecto
from django.contrib.auth.decorators import login_required

# from apps.red_vial.models import Calle, Nodo, Arco, Regulacion, NodoMovimiento, Coeficiente_Cruce
from apps.red_vial.services.red_vial_service import *
from apps.red_vial.forms.forms import   RegulacionForm, NodoMovimientoForm, CoeficienteCruceForm
from apps.red_vial.services.arco_service import get_arcos_by_proyecto
from apps.red_vial.services.calle_service import get_calles_by_proyecto
from apps.red_vial.services.nodo_service import get_nodos_by_proyecto



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