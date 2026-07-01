import json
from typing import Any

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView

from apps.proyectos.models import Proyecto
from apps.red_vial.models import Regulacion
from apps.red_vial.forms.regulacion_form import RegulacionForm
from apps.red_vial.services.regulacion_service import (
    get_all_regulaciones, create_regulacion, update_regulacion, delete_regulacion,
)


class RegulacionesListView(ListView):
    model: type = Regulacion
    context_object_name: str = 'regulaciones'
    template_name: str = 'red_vial/regulaciones_list.html'
    sort_fields: list[str] = ['codigo', 'descripcion']
    default_sort: str = 'codigo'

    @method_decorator(login_required)
    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(*args, **kwargs)

    def get_queryset(self) -> QuerySet[Regulacion]:
        sort_by = self.request.GET.get('sort_by', self.default_sort)
        sort_order = self.request.GET.get('sort_order', 'asc')
        if sort_by not in self.sort_fields:
            sort_by = self.default_sort
        return get_all_regulaciones(sort_by=sort_by, order=sort_order)

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
            return render(self.request, 'partials/Regulaciones/regulaciones_table.html', context)
        return super().render_to_response(context, **response_kwargs)


class RegulacionCreateView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['POST']))
    def post(self, request: HttpRequest) -> HttpResponse:
        form = RegulacionForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    item = create_regulacion(form.cleaned_data)
                response = render(request, 'partials/Regulaciones/regulacion_row.html', {
                    'regulacion': item,
                })
                response['HX-Trigger'] = 'regulacion-created'
                return response
            except (ValidationError, IntegrityError) as e:
                form.add_error(None, str(e))
                response = render(request, 'partials/Regulaciones/regulacion_create.html', {
                    'form': form,
                }, status=400)
                response['HX-Reswap'] = 'outerHTML'
                return response
        response = render(request, 'partials/Regulaciones/regulacion_create.html', {
            'form': form,
        }, status=400)
        response['HX-Reswap'] = 'outerHTML'
        return response


class RegulacionUpdateView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['PUT']))
    def put(self, request: HttpRequest, item_id: str) -> HttpResponse:
        from django.http import QueryDict
        try:
            data = QueryDict(request.body)
            with transaction.atomic():
                item = update_regulacion(item_id, data)
            response = render(request, 'partials/Regulaciones/regulacion_row.html', {
                'regulacion': item,
            })
            response['HX-Trigger'] = 'item-updated'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}), content_type='application/json'
            )


class RegulacionDeleteView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['DELETE']))
    def delete(self, request: HttpRequest, item_id: str) -> HttpResponse:
        try:
            with transaction.atomic():
                delete_regulacion(item_id)
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'regulacion-deleted'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}), content_type='application/json'
            )
