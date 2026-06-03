from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest, JsonResponse, QueryDict, HttpResponse

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views import View
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import json
from apps.red_vial.models import Periodizacion, PuntoControl, Periodo, Nodo
from apps.red_vial.forms.periodizacion_forms import PeriodizacionForm
from apps.red_vial.services.periodizacion_service import (
    get_periodizaciones,
    generar_filas,
    update_periodizacion,
    delete_periodizacion,
)
from apps.proyectos.models import Proyecto


@method_decorator(login_required, name='dispatch')
class PeriodizacionListView(View):
    """Lista de periodización con filtros y generación de filas."""
    template_full = 'red_vial/Periodizacion/periodizacion_list.html'
    template_table = 'partials/Periodizacion/periodizacion_table.html'

    def get(self, request, proyecto_id):
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)

        nodo_ids = request.GET.getlist('nodo')
        periodo_ids = request.GET.getlist('periodo')
        fecha = request.GET.get('fecha') or None
        sort_param = request.GET.get('sort')
        order_param = request.GET.get('order', 'asc')

        nodo_ids = [n for n in nodo_ids if n]
        periodo_ids = [p for p in periodo_ids if p]

        rows = get_periodizaciones(
            proyecto_id=proyecto_id,
            nodo_ids=nodo_ids or None,
            periodo_ids=periodo_ids or None,
            fecha=fecha,
            sort_param=sort_param,
            order_param=order_param,
        )

        available_nodos = Nodo.objects.filter(
            numero_pc__isnull=False, proyecto=proyecto
        ).select_related('calle_1', 'calle_2')
        available_periodos = Periodo.objects.filter(proyecto=proyecto)

        context = {
            'proyecto': proyecto,
            'rows': rows,
            'available_nodos': available_nodos,
            'available_periodos': available_periodos,
            'selected_nodos': nodo_ids,
            'selected_periodos': periodo_ids,
            'selected_fecha': fecha,
            'sort_param': sort_param,
            'order_param': order_param,
            'form': PeriodizacionForm(),
        }

        if request.headers.get('HX-Request'):
            return render(request, self.template_table, context)
        return render(request, self.template_full, context)

    def post(self, request, proyecto_id):
        """Genera filas de periodización."""
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)

        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            data = request.POST

        nodo_ids = data.getlist('nodo') if hasattr(data, 'getlist') else data.get('nodo_ids', [])
        periodo_ids = data.getlist('periodo') if hasattr(data, 'getlist') else data.get('periodo_ids', [])
        fecha = data.get('fecha')

        if not nodo_ids or not periodo_ids or not fecha:
            return HttpResponseBadRequest(
                json.dumps({'error': 'Debe seleccionar PC(s), Periodo(s) y Fecha'}),
                content_type='application/json',
            )

        try:
            count = generar_filas(proyecto, nodo_ids, periodo_ids, fecha)
            rows = get_periodizaciones(
                proyecto_id=proyecto_id,
                nodo_ids=nodo_ids,
                periodo_ids=periodo_ids,
                fecha=fecha,
            )
            context = {
                'proyecto': proyecto,
                'rows': rows,
                'available_nodos': Nodo.objects.filter(
                    numero_pc__isnull=False, proyecto=proyecto
                ).select_related('calle_1', 'calle_2'),
                'available_periodos': Periodo.objects.filter(proyecto=proyecto),
                'selected_nodos': nodo_ids,
                'selected_periodos': periodo_ids,
                'selected_fecha': fecha,
                'form': PeriodizacionForm(),
                'generated_count': count,
            }
            response = render(request, self.template_table, context)
            response['X-Generated-Count'] = str(count)
            return response
        except IntegrityError:
            return HttpResponseBadRequest(
                json.dumps({'error': 'Error de integridad al generar filas.'}),
                content_type='application/json',
            )


@method_decorator(login_required, name='dispatch')
class PeriodizacionUpdateView(View):
    """Actualiza un campo vehicular de una fila de periodización (PUT parcial)."""
    def put(self, request, item_id):
        print(f"Received PUT request for Periodizacion ID: {item_id}")  # Debug log
        try:
            try:
                data = json.loads(request.body) if request.body else {}
            except json.JSONDecodeError:
                data = QueryDict(request.body).dict()
            print("Parsed data from QueryDict:", data)  # Debug log


    # def put(self, request, item_id):
    #     try:
    #         data = json.loads(request.body) if request.body else {}
    #         if not data:
    #             from django.http import QueryDict
    #             data = QueryDict(request.body).dict()

            item = update_periodizacion(item_id, data)
            context = {
                'item': item,
                'form': PeriodizacionForm(instance=item),
            }
            print("Context for update response:", context)  # Debug log
            return render(request, 'partials/Periodizacion/periodizacion_row.html', context)
        except ValidationError as e:
            print("Validation error:", e)  # Debug log
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}),
                content_type='application/json',
            )


@method_decorator(login_required, name='dispatch')
class PeriodizacionDeleteView(View):
    """Elimina una fila de periodización."""

    def delete(self, request, item_id):
        try:
            delete_periodizacion(item_id)
            return HttpResponse(status=204)
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}),
                content_type='application/json',
            )
