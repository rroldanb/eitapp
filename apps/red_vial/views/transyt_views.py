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

from apps.red_vial.models.transyt import ConfiguracionTransyt, ParametroArco, FaseSemaforica
from apps.red_vial.forms.transyt_forms import ConfiguracionTransytForm, ParametroArcoForm, FaseSemaforicaForm
from apps.red_vial.services.parametro_arco_service import (
    get_parametros_by_proyecto, create_parametro_arco,
    update_parametro_arco, delete_parametro_arco,
)
from apps.red_vial.services.fase_semaforica_service import (
    get_fases_by_proyecto, create_fase_semaforica,
    update_fase_semaforica, delete_fase_semaforica,
)
from apps.proyectos.models import Proyecto


# ============ CONFIGURACIÓN TRANSYT ============

@method_decorator(login_required, name='dispatch')
class ConfiguracionTransytView(View):
    template: str = 'red_vial/configuracion_transyt.html'

    def get(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        config, _ = ConfiguracionTransyt.objects.get_or_create(
            proyecto=proyecto,
            defaults={'ciclo': 60, 'W': 10.0, 'K': 0.5, 'perdida_inicial': 2.0, 'ganancia_final': 1.0},
        )
        form = ConfiguracionTransytForm(instance=config, proyecto=proyecto)
        context = {'proyecto': proyecto, 'form': form, 'config': config}
        return render(request, self.template, context)

    def post(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        config, _ = ConfiguracionTransyt.objects.get_or_create(proyecto=proyecto)
        form = ConfiguracionTransytForm(request.POST, instance=config, proyecto=proyecto)
        if form.is_valid():
            form.save()
            context = {'proyecto': proyecto, 'form': ConfiguracionTransytForm(instance=config, proyecto=proyecto), 'config': config, 'saved': True}
            return render(request, self.template, context)
        context = {'proyecto': proyecto, 'form': form, 'config': config}
        return render(request, self.template, context, status=400)


# ============ PARÁMETROS DE ARCO ============

class ParametroArcoListView(ListView):
    model: type = ParametroArco
    context_object_name: str = 'items'
    template_name: str = 'red_vial/parametros_arco_list.html'
    paginate_by: int = 20
    sort_fields: list[str] = ['punto_control__nodo__numero_pc', 'punto_control__movimiento', 'flujo_saturacion', 'ponderador_demora', 'ponderador_detencion', 'capacidad_cola', 'tiene_tarjeta_38']
    default_sort: str = 'punto_control__nodo__numero_pc'

    @method_decorator(login_required)
    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(*args, **kwargs)

    def get_queryset(self) -> QuerySet[ParametroArco]:
        sort_by = self.request.GET.get('sort_by', self.default_sort)
        sort_order = self.request.GET.get('sort_order', 'asc')
        if sort_by not in self.sort_fields:
            sort_by = self.default_sort
        return get_parametros_by_proyecto(
            self.kwargs['proyecto_id'], sort_by=sort_by, order=sort_order
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        proyecto = get_object_or_404(
            Proyecto, id=self.kwargs['proyecto_id']
        )
        ctx['proyecto'] = proyecto
        ctx['sort_by'] = self.request.GET.get('sort_by', self.default_sort)
        ctx['sort_order'] = self.request.GET.get('sort_order', 'asc')
        ctx['sort_fields'] = self.sort_fields
        ctx['form'] = ParametroArcoForm(proyecto=proyecto)
        return ctx

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'partials/Transyt/parametro_arco_table.html', context)
        return super().render_to_response(context, **response_kwargs)


class ParametroArcoCreateView(View):
    @method_decorator(login_required)
    def get(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        form = ParametroArcoForm(proyecto=proyecto)
        return render(request, 'partials/Transyt/parametro_arco_create.html', {
            'proyecto': proyecto, 'form': form,
        })

    @method_decorator(login_required)
    @method_decorator(require_http_methods(['POST']))
    def post(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        form = ParametroArcoForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            try:
                with transaction.atomic():
                    item = create_parametro_arco(proyecto, form.cleaned_data)
                response = render(request, 'partials/Transyt/parametro_arco_row.html', {
                    'item': item, 'proyecto': proyecto,
                })
                response['HX-Trigger'] = 'parametro-arco-created'
                return response
            except (ValidationError, IntegrityError) as e:
                form.add_error(None, str(e))
                response = render(request, 'partials/Transyt/parametro_arco_create.html', {
                    'proyecto': proyecto, 'form': form,
                }, status=400)
                response['HX-Reswap'] = 'outerHTML'
                return response
        response = render(request, 'partials/Transyt/parametro_arco_create.html', {
            'proyecto': proyecto, 'form': form,
        }, status=400)
        response['HX-Reswap'] = 'outerHTML'
        return response


class ParametroArcoUpdateView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['PUT']))
    def put(self, request: HttpRequest, item_id: str) -> HttpResponse:
        from django.http import QueryDict
        try:
            data = QueryDict(request.body)
            with transaction.atomic():
                item = update_parametro_arco(item_id, data)
            response = render(request, 'partials/Transyt/parametro_arco_row.html', {
                'item': item, 'proyecto': item.proyecto,
            })
            response['HX-Trigger'] = 'item-updated'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}), content_type='application/json'
            )


class ParametroArcoDeleteView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['DELETE']))
    def delete(self, request: HttpRequest, item_id: str) -> HttpResponse:
        try:
            with transaction.atomic():
                delete_parametro_arco(item_id)
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'parametro-arco-deleted'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}), content_type='application/json'
            )


# ============ FASES SEMAFÓRICAS ============

class FaseSemaforicaListView(ListView):
    model: type = FaseSemaforica
    context_object_name: str = 'items'
    template_name: str = 'red_vial/fases_semaforicas_list.html'
    paginate_by: int = 20
    sort_fields: list[str] = ['punto_control__nodo__numero_pc', 'punto_control__movimiento', 'fase_numero', 'verde_inicio', 'verde_fin']
    default_sort: str = 'punto_control__nodo__numero_pc'

    @method_decorator(login_required)
    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(*args, **kwargs)

    def get_queryset(self) -> QuerySet[FaseSemaforica]:
        sort_by = self.request.GET.get('sort_by', self.default_sort)
        sort_order = self.request.GET.get('sort_order', 'asc')
        if sort_by not in self.sort_fields:
            sort_by = self.default_sort
        return get_fases_by_proyecto(
            self.kwargs['proyecto_id'], sort_by=sort_by, order=sort_order
        )

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        proyecto = get_object_or_404(
            Proyecto, id=self.kwargs['proyecto_id']
        )
        ctx['proyecto'] = proyecto
        ctx['sort_by'] = self.request.GET.get('sort_by', self.default_sort)
        ctx['sort_order'] = self.request.GET.get('sort_order', 'asc')
        ctx['sort_fields'] = self.sort_fields
        ctx['form'] = FaseSemaforicaForm(proyecto=proyecto)
        return ctx

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if self.request.headers.get('HX-Request'):
            return render(self.request, 'partials/Transyt/fase_semaforica_table.html', context)
        return super().render_to_response(context, **response_kwargs)


class FaseSemaforicaCreateView(View):
    @method_decorator(login_required)
    def get(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        form = FaseSemaforicaForm(proyecto=proyecto)
        return render(request, 'partials/Transyt/fase_semaforica_create.html', {
            'proyecto': proyecto, 'form': form,
        })

    @method_decorator(login_required)
    @method_decorator(require_http_methods(['POST']))
    def post(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        form = FaseSemaforicaForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            try:
                with transaction.atomic():
                    item = create_fase_semaforica(proyecto, form.cleaned_data)
                response = render(request, 'partials/Transyt/fase_semaforica_row.html', {
                    'item': item, 'proyecto': proyecto,
                })
                response['HX-Trigger'] = 'fase-semaforica-created'
                return response
            except (ValidationError, IntegrityError) as e:
                form.add_error(None, str(e))
                response = render(request, 'partials/Transyt/fase_semaforica_create.html', {
                    'proyecto': proyecto, 'form': form,
                }, status=400)
                response['HX-Reswap'] = 'outerHTML'
                return response
        response = render(request, 'partials/Transyt/fase_semaforica_create.html', {
            'proyecto': proyecto, 'form': form,
        }, status=400)
        response['HX-Reswap'] = 'outerHTML'
        return response


class FaseSemaforicaUpdateView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['PUT']))
    def put(self, request: HttpRequest, item_id: str) -> HttpResponse:
        from django.http import QueryDict
        try:
            data = QueryDict(request.body)
            with transaction.atomic():
                item = update_fase_semaforica(item_id, data)
            response = render(request, 'partials/Transyt/fase_semaforica_row.html', {
                'item': item, 'proyecto': item.proyecto,
            })
            response['HX-Trigger'] = 'item-updated'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}), content_type='application/json'
            )


class FaseSemaforicaDeleteView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['DELETE']))
    def delete(self, request: HttpRequest, item_id: str) -> HttpResponse:
        try:
            with transaction.atomic():
                delete_fase_semaforica(item_id)
            response = HttpResponse(status=204)
            response['HX-Trigger'] = 'fase-semaforica-deleted'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}), content_type='application/json'
            )