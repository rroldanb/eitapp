from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views import View
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.http import QueryDict
import json

from apps.red_vial.models.transyt import ConfiguracionTransyt, ParametroArco, FaseSemaforica
from apps.red_vial.forms.transyt_forms import ConfiguracionTransytForm, ParametroArcoForm, FaseSemaforicaForm
from apps.proyectos.models import Proyecto


# ============ CONFIGURACIÓN TRANSYT ============

@method_decorator(login_required, name='dispatch')
class ConfiguracionTransytView(View):
    template = 'red_vial/configuracion_transyt.html'

    def get(self, request, proyecto_id):
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        config, _ = ConfiguracionTransyt.objects.get_or_create(
            proyecto=proyecto,
            defaults={'ciclo': 60, 'W': 10.0, 'K': 0.5, 'perdida_inicial': 2.0, 'ganancia_final': 1.0},
        )
        form = ConfiguracionTransytForm(instance=config, proyecto=proyecto)
        context = {'proyecto': proyecto, 'form': form, 'config': config}
        return render(request, self.template, context)

    def post(self, request, proyecto_id):
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

@method_decorator(login_required, name='dispatch')
class ParametroArcoListView(View):
    template_full = 'red_vial/parametros_arco_list.html'
    template_table = 'partials/Transyt/parametro_arco_table.html'
    sort_fields = ['punto_control__nodo__numero', 'punto_control__movimiento', 'flujo_saturacion', 'ponderador_demora', 'ponderador_detencion', 'capacidad_cola', 'tiene_tarjeta_38']
    default_sort = 'punto_control__nodo__numero'

    def get(self, request, proyecto_id):
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)

        sort_by = request.GET.get('sort_by', self.default_sort)
        sort_order = request.GET.get('sort_order', 'asc')
        if sort_by not in self.sort_fields:
            sort_by = self.default_sort
        if sort_order not in ['asc', 'desc']:
            sort_order = 'asc'

        order_prefix = '-' if sort_order == 'desc' else ''
        items = ParametroArco.objects.filter(proyecto=proyecto).select_related('punto_control__nodo').order_by(f'{order_prefix}{sort_by}')

        form = ParametroArcoForm(proyecto=proyecto)
        context = {'proyecto': proyecto, 'items': items, 'form': form, 'sort_by': sort_by, 'sort_order': sort_order, 'sort_fields': self.sort_fields}
        if request.headers.get('HX-Request'):
            return render(request, self.template_table, context)
        return render(request, self.template_full, context)


@method_decorator(login_required, name='dispatch')
@method_decorator(require_http_methods(['POST']), name='dispatch')
class ParametroArcoCreateView(View):
    def post(self, request, proyecto_id):
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        form = ParametroArcoForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            try:
                item = form.save()
                form = ParametroArcoForm(proyecto=proyecto)
                context = {'item': item, 'proyecto': proyecto, 'form': form}
                return render(request, 'partials/Transyt/parametro_arco_row.html', context)
            except IntegrityError:
                form.add_error('punto_control', 'Ya existe un parámetro para este Punto de Control.')
        context = {'proyecto': proyecto, 'form': form}
        return render(request, 'partials/Transyt/parametro_arco_create.html', context, status=400)


@method_decorator(login_required, name='dispatch')
@method_decorator(require_http_methods(['PUT']), name='dispatch')
class ParametroArcoUpdateView(View):
    def put(self, request, item_id):
        item = get_object_or_404(ParametroArco, id=item_id)
        proyecto = item.proyecto
        data = QueryDict(request.body).dict()
        form = ParametroArcoForm(data, instance=item, proyecto=proyecto)
        if form.is_valid():
            try:
                item = form.save()
                context = {'item': item, 'proyecto': proyecto, 'form': ParametroArcoForm(proyecto=proyecto)}
                return render(request, 'partials/Transyt/parametro_arco_row.html', context)
            except IntegrityError:
                form.add_error('punto_control', 'Ya existe un parámetro para este Punto de Control.')
        return HttpResponseBadRequest(json.dumps({'error': str(form.errors)}), content_type='application/json')


@method_decorator(login_required, name='dispatch')
@method_decorator(require_http_methods(['DELETE']), name='dispatch')
class ParametroArcoDeleteView(View):
    def delete(self, request, item_id):
        try:
            item = get_object_or_404(ParametroArco, id=item_id)
            item.delete()
            return HttpResponse(status=204)
        except ValidationError as e:
            return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type='application/json')


# ============ FASES SEMAFÓRICAS ============

@method_decorator(login_required, name='dispatch')
class FaseSemaforicaListView(View):
    template_full = 'red_vial/fases_semaforicas_list.html'
    template_table = 'partials/Transyt/fase_semaforica_table.html'
    sort_fields = ['punto_control__nodo__numero', 'punto_control__movimiento', 'fase_numero', 'verde_inicio', 'verde_fin']
    default_sort = 'punto_control__nodo__numero'

    def get(self, request, proyecto_id):
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)

        sort_by = request.GET.get('sort_by', self.default_sort)
        sort_order = request.GET.get('sort_order', 'asc')
        if sort_by not in self.sort_fields:
            sort_by = self.default_sort
        if sort_order not in ['asc', 'desc']:
            sort_order = 'asc'

        order_prefix = '-' if sort_order == 'desc' else ''
        items = FaseSemaforica.objects.filter(proyecto=proyecto).select_related('punto_control__nodo').order_by(f'{order_prefix}{sort_by}')

        form = FaseSemaforicaForm(proyecto=proyecto)
        context = {'proyecto': proyecto, 'items': items, 'form': form, 'sort_by': sort_by, 'sort_order': sort_order, 'sort_fields': self.sort_fields}
        if request.headers.get('HX-Request'):
            return render(request, self.template_table, context)
        return render(request, self.template_full, context)


@method_decorator(login_required, name='dispatch')
@method_decorator(require_http_methods(['POST']), name='dispatch')
class FaseSemaforicaCreateView(View):
    def post(self, request, proyecto_id):
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        form = FaseSemaforicaForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            try:
                item = form.save()
                form = FaseSemaforicaForm(proyecto=proyecto)
                context = {'item': item, 'proyecto': proyecto, 'form': form}
                return render(request, 'partials/Transyt/fase_semaforica_row.html', context)
            except IntegrityError:
                form.add_error('fase_numero', 'Ya existe una fase con ese número para este Punto de Control.')
        context = {'proyecto': proyecto, 'form': form}
        return render(request, 'partials/Transyt/fase_semaforica_create.html', context, status=400)


@method_decorator(login_required, name='dispatch')
@method_decorator(require_http_methods(['PUT']), name='dispatch')
class FaseSemaforicaUpdateView(View):
    def put(self, request, item_id):
        item = get_object_or_404(FaseSemaforica, id=item_id)
        proyecto = item.proyecto
        data = QueryDict(request.body).dict()
        form = FaseSemaforicaForm(data, instance=item, proyecto=proyecto)
        if form.is_valid():
            try:
                item = form.save()
                context = {'item': item, 'proyecto': proyecto, 'form': FaseSemaforicaForm(proyecto=proyecto)}
                return render(request, 'partials/Transyt/fase_semaforica_row.html', context)
            except IntegrityError:
                form.add_error('fase_numero', 'Ya existe una fase con ese número para este Punto de Control.')
        return HttpResponseBadRequest(json.dumps({'error': str(form.errors)}), content_type='application/json')


@method_decorator(login_required, name='dispatch')
@method_decorator(require_http_methods(['DELETE']), name='dispatch')
class FaseSemaforicaDeleteView(View):
    def delete(self, request, item_id):
        try:
            item = get_object_or_404(FaseSemaforica, id=item_id)
            item.delete()
            return HttpResponse(status=204)
        except ValidationError as e:
            return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type='application/json')
