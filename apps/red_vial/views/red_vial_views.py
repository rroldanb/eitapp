from typing import Any
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from apps.proyectos.models import Proyecto
from django.contrib.auth.decorators import login_required

from apps.red_vial.services.red_vial_service import *
from apps.red_vial.forms.regulacion_form import RegulacionForm
from apps.red_vial.forms.coeficiente_cruce_form import CoeficienteCruceForm
from apps.red_vial.services.arco_service import get_arcos_by_proyecto
from apps.red_vial.services.calle_service import get_calles_by_proyecto
from apps.red_vial.services.nodo_service import get_nodos_by_proyecto



# ========== REGULACIONES VIEWS ==========

@login_required
def regulaciones_list_view(request: HttpRequest) -> HttpResponse:
    """Vista de lista de tipos de regulación"""
    regulaciones = get_all_regulaciones()
    return render(request, 'red_vial/regulaciones_list.html', {
        'regulaciones': regulaciones
    })


@login_required
def regulacion_create_view(request: HttpRequest) -> HttpResponse:
    """Vista para crear un nuevo tipo de regulación"""
    if request.method == 'POST':
        form = RegulacionForm(request.POST)
        if form.is_valid():
            regulacion = regulacion_create(form.cleaned_data)
            return redirect('regulaciones_list')
    else:
        form = RegulacionForm()
    return render(request, 'red_vial/regulacion_form.html', {'form': form})


@login_required
def regulacion_update_view(request: HttpRequest, regulacion_id: str) -> HttpResponse:
    """Vista para editar un tipo de regulación"""
    regulacion = get_regulacion_by_id(regulacion_id)
    if request.method == 'POST':
        form = RegulacionForm(request.POST, instance=regulacion)
        if form.is_valid():
            form.save()
            return redirect('regulaciones_list')
    else:
        form = RegulacionForm(instance=regulacion)
    return render(request, 'red_vial/regulacion_form.html', {'form': form, 'regulacion': regulacion})


@login_required
def regulacion_delete_view(request: HttpRequest, regulacion_id: str) -> HttpResponse:
    """Vista para eliminar un tipo de regulación"""
    regulacion_delete(regulacion_id)
    return redirect('regulaciones_list')


# ========== COEFICIENTE CRUCE VIEWS ==========

@login_required
def coeficientes_list_view(request: HttpRequest) -> HttpResponse:
    """Vista de lista de coeficientes de cruce"""
    coeficientes = get_all_coeficientes()
    return render(request, 'red_vial/coeficientes_list.html', {
        'coeficientes': coeficientes
    })


@login_required
def coeficiente_create_view(request: HttpRequest) -> HttpResponse:
    """Vista para crear un nuevo coeficiente de cruce"""
    if request.method == 'POST':
        form = CoeficienteCruceForm(request.POST)
        if form.is_valid():
            coeficiente = coeficiente_create(form.cleaned_data)
            return redirect('coeficientes_list')
    else:
        form = CoeficienteCruceForm()
    return render(request, 'red_vial/coeficiente_form.html', {'form': form})


# ========== API / JSON ENDPOINTS ==========

@login_required
def get_arcos_api(request: HttpRequest, proyecto_id: str) -> HttpResponse:
    """API que retorna arcos de un proyecto en JSON"""
    arcos = get_arcos_by_proyecto(proyecto_id)
    data = [{'id': str(a.id), 'codigo': a.codigo_arco} for a in arcos]
    return JsonResponse(data, safe=False)


@login_required
def get_nodos_api(request: HttpRequest, proyecto_id: str) -> HttpResponse:
    nodos = get_nodos_by_proyecto(proyecto_id)
    data = [{'id': str(n.id), 'numero': n.numero, 'nombre': str(n)} for n in nodos]
    return JsonResponse(data, safe=False)


@login_required
def get_calles_api(request: HttpRequest, proyecto_id: str) -> HttpResponse:
    calles = get_calles_by_proyecto(proyecto_id)
    data = [{'id': str(c.id), 'numero': c.numero, 'nombre': c.nombre} for c in calles]
    return JsonResponse(data, safe=False)
