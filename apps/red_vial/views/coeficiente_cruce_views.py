import json
from typing import Any

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView

from apps.proyectos.models import Proyecto
from apps.red_vial.models import CoeficienteCruce
from apps.red_vial.forms.coeficiente_cruce_form import CoeficienteCruceModelForm
from apps.red_vial.services.coeficiente_cruce_service import (
    get_all_coeficientes_cruce, create_coeficiente_cruce,
    update_coeficiente_cruce, delete_coeficiente_cruce,
)


class CoeficientesCruceListView(ListView):
    model: type = CoeficienteCruce
    context_object_name: str = 'coeficientes'
    template_name: str = 'red_vial/coeficientes_cruce_list.html'
    paginate_by: int = 20
    sort_fields: list[str] = ['nomenclatura', 'tipo_transporte', 'coeficiente', 'proyecto']
    default_sort: str = 'nomenclatura'

    @method_decorator(login_required)
    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(*args, **kwargs)

    def get_queryset(self) -> QuerySet[CoeficienteCruce]:
        sort_by = self.request.GET.get('sort_by', self.default_sort)
        sort_order = self.request.GET.get('sort_order', 'asc')
        if sort_by not in self.sort_fields:
            sort_by = self.default_sort
        return get_all_coeficientes_cruce(sort_by=sort_by, order=sort_order)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        proyecto_id = self.kwargs.get('proyecto_id')
        if proyecto_id:
            ctx['proyecto'] = get_object_or_404(Proyecto, id=proyecto_id)
        ctx['sort_by'] = self.request.GET.get('sort_by', self.default_sort)
        ctx['sort_order'] = self.request.GET.get('sort_order', 'asc')
        ctx['sort_fields'] = self.sort_fields
        return ctx

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'partials/CoeficientesCruce/coeficientes_cruce_table.html', context)
        return super().render_to_response(context, **response_kwargs)


class CoeficienteCruceCreateView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['POST']))
    def post(self, request: HttpRequest, proyecto_id: str | None = None) -> HttpResponse:
        form = CoeficienteCruceModelForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    item = create_coeficiente_cruce(form.cleaned_data)
                response = render(request, 'partials/CoeficientesCruce/coeficiente_cruce_row.html', {
                    'item': item,
                })
                response['HX-Trigger'] = 'coeficiente-cruce-created'
                return response
            except ValidationError as e:
                form.add_error(None, str(e))
                response = render(request, 'partials/CoeficientesCruce/coeficiente_cruce_create.html', {
                    'form': form,
                }, status=400)
                response['HX-Reswap'] = 'outerHTML'
                return response
        response = render(request, 'partials/CoeficientesCruce/coeficiente_cruce_create.html', {
            'form': form,
        }, status=400)
        response['HX-Reswap'] = 'outerHTML'
        return response


class CoeficienteCruceUpdateView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['PUT']))
    def put(self, request: HttpRequest, item_id: str) -> HttpResponse:
        from django.http import QueryDict
        try:
            data = QueryDict(request.body)
            with transaction.atomic():
                item = update_coeficiente_cruce(item_id, data)
            response = render(request, 'partials/CoeficientesCruce/coeficiente_cruce_row.html', {
                'item': item,
            })
            response['HX-Trigger'] = 'item-updated'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}), content_type='application/json'
            )


class CoeficienteCruceDeleteView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['DELETE']))
    def delete(self, request: HttpRequest, item_id: str) -> HttpResponse:
        try:
            with transaction.atomic():
                delete_coeficiente_cruce(item_id)
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'coeficiente-cruce-deleted'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}), content_type='application/json'
            )
