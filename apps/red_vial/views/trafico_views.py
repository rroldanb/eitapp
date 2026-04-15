from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from apps.proyectos.models import Proyecto
from apps.red_vial.services.trafico_service import *
from apps.red_vial.services.red_vial_service import (
    get_nodos_movimientos_by_proyecto,
    get_nodos_by_proyecto
)
from apps.red_vial.trafico_forms import (
    PeriodoForm,
    ConteoVehicularForm,
    FlujoMovimientoForm,
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


# ========== CONTEO VEHICULAR VIEWS ==========

@login_required
def conteos_list_view(request, proyecto_id):
    """Vista de lista de conteos vehiculares de un proyecto"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    conteos = get_conteos_by_proyecto(proyecto_id)
    return render(request, 'red_vial/conteos_list.html', {
        'proyecto': proyecto,
        'conteos': conteos
    })


@login_required
def conteo_detail_view(request, conteo_id):
    """Vista detalle de un conteo vehicular"""
    conteo = get_conteo_by_id(conteo_id)
    return render(request, 'red_vial/conteo_detail.html', {
        'conteo': conteo
    })


@login_required
def conteo_create_view(request, proyecto_id):
    """Vista para crear un nuevo conteo vehicular"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    if request.method == 'POST':
        form = ConteoVehicularForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            conteo = form.save(commit=False)
            conteo.proyecto = proyecto
            conteo.save()
            return redirect('conteos_list', proyecto_id=proyecto_id)
    else:
        form = ConteoVehicularForm(proyecto=proyecto)

    return render(request, 'red_vial/conteo_form.html', {
        'proyecto': proyecto,
        'form': form
    })


@login_required
def conteo_update_view(request, conteo_id):
    """Vista para actualizar un conteo vehicular"""
    conteo = get_conteo_by_id(conteo_id)

    if request.method == 'POST':
        form = ConteoVehicularForm(request.POST, instance=conteo, proyecto=conteo.proyecto)
        if form.is_valid():
            form.save()
            return redirect('conteos_list', proyecto_id=conteo.proyecto.id)
    else:
        form = ConteoVehicularForm(instance=conteo, proyecto=conteo.proyecto)

    return render(request, 'red_vial/conteo_form.html', {
        'proyecto': conteo.proyecto,
        'form': form,
        'conteo': conteo
    })


@login_required
def conteo_delete_view(request, conteo_id):
    """Vista para eliminar un conteo vehicular"""
    conteo = get_conteo_by_id(conteo_id)
    proyecto_id = conteo.proyecto.id
    conteo_delete(conteo_id)
    return redirect('conteos_list', proyecto_id=proyecto_id)


# ========== FLUJO MOVIMIENTO VIEWS ==========

@login_required
def flujos_list_view(request, proyecto_id):
    """Vista de lista de flujos de movimiento"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    flujos = get_flujos_by_proyecto(proyecto_id)
    return render(request, 'red_vial/flujos_list.html', {
        'proyecto': proyecto,
        'flujos': flujos
    })


@login_required
def flujo_create_view(request, proyecto_id):
    """Vista para crear un nuevo flujo de movimiento"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    if request.method == 'POST':
        form = FlujoMovimientoForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            flujo = form.save(commit=False)
            flujo.proyecto = proyecto
            flujo.save()
            return redirect('flujos_list', proyecto_id=proyecto_id)
    else:
        form = FlujoMovimientoForm(proyecto=proyecto)

    return render(request, 'red_vial/flujo_form.html', {
        'proyecto': proyecto,
        'form': form
    })


@login_required
def flujo_update_view(request, flujo_id):
    """Vista para actualizar un flujo de movimiento"""
    flujo = get_flujo_by_id(flujo_id)

    if request.method == 'POST':
        form = FlujoMovimientoForm(request.POST, instance=flujo, proyecto=flujo.proyecto)
        if form.is_valid():
            form.save()
            return redirect('flujos_list', proyecto_id=flujo.proyecto.id)
    else:
        form = FlujoMovimientoForm(instance=flujo, proyecto=flujo.proyecto)

    return render(request, 'red_vial/flujo_form.html', {
        'proyecto': flujo.proyecto,
        'form': form,
        'flujo': flujo
    })


@login_required
def flujo_delete_view(request, flujo_id):
    """Vista para eliminar un flujo de movimiento"""
    flujo = get_flujo_by_id(flujo_id)
    proyecto_id = flujo.proyecto.id
    flujo_delete(flujo_id)
    return redirect('flujos_list', proyecto_id=proyecto_id)


# ========== ANALYSIS VIEWS ==========

@login_required
def analisis_trafico_view(request, proyecto_id):
    """Vista de análisis de tráfico"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    periodos = get_all_periodos()

    # Obtener promedios por período como lista
    promedios_list = []
    for periodo in periodos:
        datos = get_flujo_promedio_por_periodo(proyecto_id, periodo.id)
        promedios_list.append({
            'periodo': periodo,
            'promedio_veh_hora': datos.get('promedio_veh_hora'),
            'promedio_veq_hora': datos.get('promedio_veq_hora'),
        })

    # Top nodos con mayor flujo
    top_nodos = get_nodos_con_mayor_flujo(proyecto_id, limit=10)

    return render(request, 'red_vial/analisis_trafico.html', {
        'proyecto': proyecto,
        'promedios_list': promedios_list,
        'top_nodos': top_nodos,
    })


# ========== API VIEWS (JSON) ==========

@login_required
def api_periodos(request):
    """API endpoint para obtener todos los períodos"""
    periodos = get_all_periodos()
    data = [{
        'id': str(p.id),
        'codigo': p.codigo,
        'nombre': p.nombre,
        'tipo_dia': p.tipo_dia
    } for p in periodos]
    return JsonResponse({'periodos': data})


@login_required
def api_conteos_by_proyecto(request, proyecto_id):
    """API endpoint para obtener conteos de un proyecto"""
    conteos = get_conteos_by_proyecto(proyecto_id)
    data = [{
        'id': str(c.id),
        'nodo': c.nodo.numero if c.nodo else None,
        'periodo': c.periodo.codigo if c.periodo else None,
        'hora': c.hora.strftime('%H:%M') if c.hora else None,
        'veq': c.vehiculos_equivalentes
    } for c in conteos]
    return JsonResponse({'conteos': data})


@login_required
def api_flujos_by_proyecto(request, proyecto_id):
    """API endpoint para obtener flujos de un proyecto"""
    flujos = get_flujos_by_proyecto(proyecto_id)
    data = [{
        'id': str(f.id),
        'nodo_movimiento': str(f.nodo_movimiento),
        'periodo': f.periodo.codigo if f.periodo else None,
        'hora': f.hora.strftime('%H:%M') if f.hora else None,
        'flujo_veq_hora': f.flujo_veq_hora
    } for f in flujos]
    return JsonResponse({'flujos': data})


@login_required
def api_analisis_promedios(request, proyecto_id):
    """API endpoint para obtener promedios de tráfico"""
    from django.db.models import Avg
    from apps.red_vial.models import ConteoVehicular

    promedios = ConteoVehicular.objects.filter(
        proyecto_id=proyecto_id
    ).values('periodo__codigo').annotate(
        avg_veq=Avg('vehiculos_equivalentes'),
        avg_vl=Avg('vl'),
        avg_txb=Avg('txb')
    )

    return JsonResponse({'promedios': list(promedios)})
