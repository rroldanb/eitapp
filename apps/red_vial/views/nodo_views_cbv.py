from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.http import JsonResponse

from apps.red_vial.models import Nodo
from apps.red_vial.forms.nodo_form import NodoForm
from apps.red_vial.services.nodo_service import (
    get_nodos_by_proyecto,
    create_nodo,
    update_nodo,
    delete_nodo,
    bulk_update_nodos,
    update_nodo_image,
    delete_nodo_image,
    update_nodo_plano,
    delete_nodo_plano,
)
from apps.imagenes.utils.image_processor import get_image_from_request

from .generic_views import (
    GenericListView,
    GenericCreateView,
    GenericUpdateView,
    GenericDeleteView,
    GenericBulkUpdateView,
)


def _nodo_handle_file_upload(request, item_id, update_fn):
    nodo = get_object_or_404(Nodo, id=item_id)
    try:
        file = get_image_from_request(request)
        if not file:
            return JsonResponse({'success': False, 'error': 'No se proporcionó imagen'}, status=400)
        nodo = update_fn(nodo.id, file)
        return render(request, 'partials/Nodos/nodo_row.html', {
            'nodo': nodo,
            'proyecto': nodo.proyecto,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def _nodo_handle_file_delete(request, item_id, delete_fn):
    nodo = get_object_or_404(Nodo, id=item_id)
    try:
        nodo = delete_fn(nodo.id)
        return render(request, 'partials/Nodos/nodo_row.html', {
            'nodo': nodo,
            'proyecto': nodo.proyecto,
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def nodo_upload_image_view(request, item_id):
    return _nodo_handle_file_upload(request, item_id, update_nodo_image)


@login_required
@require_POST
def nodo_delete_image_view(request, item_id):
    return _nodo_handle_file_delete(request, item_id, delete_nodo_image)


@login_required
@require_POST
def nodo_upload_plano_view(request, item_id):
    return _nodo_handle_file_upload(request, item_id, update_nodo_plano)


@login_required
@require_POST
def nodo_delete_plano_view(request, item_id):
    return _nodo_handle_file_delete(request, item_id, delete_nodo_plano)


@login_required
@require_GET
def nodo_images_json_view(request, item_id):
    nodo = get_object_or_404(Nodo, id=item_id)
    return JsonResponse({
        'imagen': nodo.imagen or '',
        'plano': nodo.plano or '',
    })


class NodosListView(GenericListView):
    model = Nodo
    service_get_function = get_nodos_by_proyecto
    sort_fields = ['numero', 'calle_1', 'calle_2', 'is_pc']
    default_sort = 'numero'
    partial_template = 'partials/Nodos/nodos_table.html'
    full_template = 'red_vial/nodos_list.html'
    context_items_key = 'nodos'


class NodosCreateView(GenericCreateView):
    model = Nodo
    form_class = NodoForm
    service_create_function = create_nodo
    row_template = 'partials/Nodos/nodo_row.html'
    form_template = 'partials/Nodos/nodo_create.html'


class NodosUpdateView(GenericUpdateView):
    model = Nodo
    service_update_function = update_nodo
    row_template = 'partials/Nodos/nodo_row.html'


class NodosDeleteView(GenericDeleteView):
    model = Nodo
    service_delete_function = delete_nodo


class NodosBulkUpdateView(GenericBulkUpdateView):
    service_bulk_update = bulk_update_nodos
