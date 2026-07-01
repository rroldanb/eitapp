import json
from typing import Any

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import render, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_POST, require_GET, require_http_methods
from django.views.generic import ListView

from apps.proyectos.models import Proyecto
from apps.red_vial.models import Nodo
from apps.red_vial.forms.nodo_form import NodoForm
from apps.red_vial.services.nodo_service import (
    get_nodos_by_proyecto,
    create_nodo,
    update_nodo,
    delete_nodo,
    update_nodo_image,
    delete_nodo_image,
    update_nodo_plano,
    delete_nodo_plano,
)
from apps.imagenes.utils.image_processor import get_image_from_request


def _nodo_handle_file_upload(request: HttpRequest, item_id: str, update_fn: Any) -> HttpResponse:
    nodo = get_object_or_404(Nodo, id=item_id)
    try:
        file = get_image_from_request(request)
        if not file:
            return JsonResponse({'success': False, 'error': 'No se proporcionó imagen'}, status=400)
        nodo = update_fn(nodo.id, file)
        return render(request, 'partials/Nodos/nodo_row.html', {
            'nodo': nodo, 'proyecto': nodo.proyecto,
            'calles': nodo.proyecto.calles.all(),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


def _nodo_handle_file_delete(request: HttpRequest, item_id: str, delete_fn: Any) -> HttpResponse:
    nodo = get_object_or_404(Nodo, id=item_id)
    try:
        nodo = delete_fn(nodo.id)
        return render(request, 'partials/Nodos/nodo_row.html', {
            'nodo': nodo, 'proyecto': nodo.proyecto,
            'calles': nodo.proyecto.calles.all(),
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def nodo_upload_image_view(request: HttpRequest, item_id: str) -> HttpResponse:
    return _nodo_handle_file_upload(request, item_id, update_nodo_image)


@login_required
@require_POST
def nodo_delete_image_view(request: HttpRequest, item_id: str) -> HttpResponse:
    return _nodo_handle_file_delete(request, item_id, delete_nodo_image)


@login_required
@require_POST
def nodo_upload_plano_view(request: HttpRequest, item_id: str) -> HttpResponse:
    return _nodo_handle_file_upload(request, item_id, update_nodo_plano)


@login_required
@require_POST
def nodo_delete_plano_view(request: HttpRequest, item_id: str) -> HttpResponse:
    return _nodo_handle_file_delete(request, item_id, delete_nodo_plano)


@login_required
@require_GET
def nodo_images_json_view(request: HttpRequest, item_id: str) -> JsonResponse:
    nodo = get_object_or_404(Nodo, id=item_id)
    return JsonResponse({
        'imagen': nodo.imagen or '',
        'plano': nodo.plano or '',
        'nombre': str(nodo),
    })


class NodosListView(ListView):
    model: type = Nodo
    context_object_name: str = 'nodos'
    template_name: str = 'red_vial/nodos_list.html'
    paginate_by: int = 20
    sort_fields: list[str] = ['numero', 'calle_1', 'calle_2', 'is_pc', 'numero_pc']
    default_sort: str = 'numero'

    @method_decorator(login_required)
    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(*args, **kwargs)

    def get_queryset(self) -> QuerySet[Nodo]:
        sort_by = self.request.GET.get('sort_by', self.default_sort)
        sort_order = self.request.GET.get('sort_order', 'asc')
        if sort_by not in self.sort_fields:
            sort_by = self.default_sort
        return get_nodos_by_proyecto(
            self.kwargs['proyecto_id'], sort_by=sort_by, order=sort_order
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx['proyecto'] = get_object_or_404(
            Proyecto, id=self.kwargs['proyecto_id']
        )
        ctx['sort_by'] = self.request.GET.get('sort_by', self.default_sort)
        ctx['sort_order'] = self.request.GET.get('sort_order', 'asc')
        ctx['sort_fields'] = self.sort_fields
        return ctx

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'partials/Nodos/nodos_table.html', context)
        return super().render_to_response(context, **response_kwargs)


class NodoCreateView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['POST']))
    def post(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        form = NodoForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            try:
                with transaction.atomic():
                    nodo = create_nodo(proyecto, form.cleaned_data)
                response = render(request, 'partials/Nodos/nodo_row.html', {
                    'nodo': nodo, 'proyecto': proyecto,
                    'calles': proyecto.calles.all(),
                })
                response['HX-Trigger'] = 'nodo-created'
                return response
            except (ValidationError, IntegrityError) as e:
                form.add_error(None, str(e))
                response = render(request, 'partials/Nodos/nodo_create.html', {
                    'proyecto': proyecto, 'form': form,
                }, status=400)
                response['HX-Reswap'] = 'outerHTML'
                return response
        response = render(request, 'partials/Nodos/nodo_create.html', {
            'proyecto': proyecto, 'form': form,
        }, status=400)
        response['HX-Reswap'] = 'outerHTML'
        return response


class NodoUpdateView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['PUT']))
    def put(self, request: HttpRequest, item_id: str) -> HttpResponse:
        from django.http import QueryDict
        try:
            data = QueryDict(request.body)
            with transaction.atomic():
                nodo = update_nodo(item_id, data)
            response = render(request, 'partials/Nodos/nodo_row.html', {
                'nodo': nodo, 'proyecto': nodo.proyecto,
                'calles': nodo.proyecto.calles.all(),
            })
            response['HX-Trigger'] = 'item-updated'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}), content_type='application/json'
            )


class NodoDeleteView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['DELETE']))
    def delete(self, request: HttpRequest, item_id: str) -> HttpResponse:
        try:
            with transaction.atomic():
                delete_nodo(item_id)
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'nodo-deleted'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}), content_type='application/json'
            )
