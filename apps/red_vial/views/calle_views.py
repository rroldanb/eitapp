from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse, HttpResponseBadRequest, HttpResponseServerError, QueryDict
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from apps.proyectos.models import Proyecto
from apps.red_vial.models import Calle
from apps.red_vial.forms.forms import CalleForm
from apps.red_vial.services.calle_service import get_calles_by_proyecto, get_calle_by_id, bulk_update_calles
import json


# ========== CALLE VIEWS ==========

@login_required
def calles_list_view(request, proyecto_id):
    """Lista de calles de un proyecto."""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    sort_by = request.GET.get('sort_by', 'numero')
    sort_order = request.GET.get('sort_order', 'asc')
    if sort_order not in ['asc', 'desc']:
        sort_order = 'asc'

    calles = get_calles_by_proyecto(proyecto_id, sort_by=sort_by, order=sort_order)
    context = {
        'proyecto': proyecto,
        'calles': calles,
        'next_numero': proyecto.calles.count() + 1,
        'sort_by': sort_by,
        'sort_order': sort_order,
        'active_section': 'calles'
    }

    if request.headers.get('HX-Request'):
        return render(request, 'partials/Calles/calles_table.html', context)

    return render(request, 'red_vial/Calles/calles_list.html', context)


@login_required
@require_http_methods(['POST'])
def calle_create_view(request, proyecto_id):
    """Crear una calle nueva para un proyecto."""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    form = CalleForm(request.POST)

    if form.is_valid():
        calle = form.save(commit=False)
        calle.proyecto = proyecto
        calle.save()
        return render(request, 'partials/Calles/calle_row.html', {'calle': calle})

    return render(request, 'partials/Calles/calle_create_form.html', {
        'proyecto': proyecto,
        'form': form,
        'next_numero': proyecto.calles.count() + 1
    }, status=400)


@login_required
@require_http_methods(['PUT'])
def calle_update_view(request, calle_id):
    """Actualizar una calle existente."""
    calle = get_object_or_404(Calle, id=calle_id)
    data = QueryDict(request.body)
    form = CalleForm(data, instance=calle)

    if form.is_valid():
        calle = form.save()
        response = render(request, 'partials/Calles/calle_row.html', {'calle': calle})
        response['HX-Trigger'] = f'calle-updated:{calle.id}'
        return response

    return HttpResponseBadRequest(form.errors.as_json(), content_type='application/json')


@login_required
@require_http_methods(['DELETE'])
def calle_delete_view(request, calle_id):
    """Eliminar una calle."""
    calle = get_object_or_404(Calle, id=calle_id)
    proyecto_id = calle.proyecto.id
    calle.delete()

    if request.headers.get('HX-Request'):
        return HttpResponse(status=204)
    return redirect('calles_list', proyecto_id=proyecto_id)


@login_required
@require_http_methods(['POST'])
def calles_bulk_update_view(request, proyecto_id):
    """Actualizar múltiples calles en lote."""
    try:
        data_list = json.loads(request.body)
        updated_ids = bulk_update_calles(data_list)
        return JsonResponse({
            'success': True,
            'updated_count': len(updated_ids),
            'updated_ids': updated_ids
        })
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
