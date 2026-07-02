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
from apps.red_vial.models import Periodo
from apps.red_vial.forms.periodo_form import PeriodoForm
from apps.red_vial.services.periodo_service import (
    get_periodos_by_proyecto, create_periodo, update_periodo, delete_periodo,
)


class PeriodoListView(ListView):
    model: type = Periodo
    context_object_name: str = 'periodos'
    template_name: str = 'red_vial/periodo_list.html'
    paginate_by: int = 20
    sort_fields: list[str] = ['codigo', 'hora_inicio', 'hora_fin', 'es_laboral']
    default_sort: str = 'codigo'

    @method_decorator(login_required)
    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(*args, **kwargs)

    def get_queryset(self) -> QuerySet[Periodo]:
        sort_by = self.request.GET.get('sort_by', self.default_sort)
        sort_order = self.request.GET.get('sort_order', 'asc')
        if sort_by not in self.sort_fields:
            sort_by = self.default_sort
        return get_periodos_by_proyecto(
            self.kwargs['proyecto_id'], sort_by=sort_by, order=sort_order
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        proyecto = get_object_or_404(
            Proyecto, id=self.kwargs['proyecto_id']
        )
        ctx['proyecto'] = proyecto
        ctx['form'] = PeriodoForm(proyecto=proyecto)
        ctx['sort_by'] = self.request.GET.get('sort_by', self.default_sort)
        ctx['sort_order'] = self.request.GET.get('sort_order', 'asc')
        ctx['sort_fields'] = self.sort_fields
        return ctx

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'partials/Periodo/periodo_table.html', context)
        return super().render_to_response(context, **response_kwargs)


class PeriodoCreateView(View):
    @method_decorator(login_required)
    def get(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        form = PeriodoForm(proyecto=proyecto)
        return render(request, 'partials/Periodo/periodo_create.html', {
            'proyecto': proyecto, 'form': form,
        })

    @method_decorator(login_required)
    @method_decorator(require_http_methods(['POST']))
    def post(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        form = PeriodoForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            try:
                with transaction.atomic():
                    periodo = create_periodo(proyecto, form.cleaned_data)
                response = render(request, 'partials/Periodo/periodo_row.html', {
                    'periodo': periodo, 'proyecto': proyecto,
                })
                response['HX-Trigger'] = 'periodo-created'
                return response
            except (ValidationError, IntegrityError) as e:
                form.add_error(None, str(e))
                response = render(request, 'partials/Periodo/periodo_create.html', {
                    'proyecto': proyecto, 'form': form,
                }, status=400)
                response['HX-Reswap'] = 'outerHTML'
                return response
        response = render(request, 'partials/Periodo/periodo_create.html', {
            'proyecto': proyecto, 'form': form,
        }, status=400)
        response['HX-Reswap'] = 'outerHTML'
        return response


class PeriodoUpdateView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['PUT']))
    def put(self, request: HttpRequest, item_id: str) -> HttpResponse:
        from django.http import QueryDict
        try:
            data = QueryDict(request.body)
            with transaction.atomic():
                periodo = update_periodo(item_id, data)
            response = render(request, 'partials/Periodo/periodo_row.html', {
                'periodo': periodo, 'proyecto': periodo.proyecto,
            })
            response['HX-Trigger'] = 'item-updated'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}), content_type='application/json'
            )


class PeriodoDeleteView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['DELETE']))
    def delete(self, request: HttpRequest, item_id: str) -> HttpResponse:
        try:
            with transaction.atomic():
                delete_periodo(item_id)
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'periodo-deleted'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}), content_type='application/json'
            )
