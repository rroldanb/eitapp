import json
from typing import Any

from django.shortcuts import render, get_object_or_404
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods

from apps.proyectos.models import Proyecto
from apps.red_vial.models import Nodo, Periodo, PuntoControl, Periodizacion
from apps.red_vial.services.resumen_flujo_service import (
    recalcular_resumenes,
    get_analisis_flujos,
    get_ranking,
    get_comparison,
    get_chart_data,
)


@method_decorator(login_required, name='dispatch')
class AnalisisFlujosView(View):
    template_full = 'red_vial/analisis_flujos.html'
    template_container = 'partials/analisis_flujos/analisis_flujos_container.html'

    def get(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)

        nodo_ids = request.GET.getlist('nodo')
        periodo_ids = request.GET.getlist('periodo')
        movimiento_ids = request.GET.getlist('movimiento')
        fecha = request.GET.get('fecha') or None

        nodo_ids = [n for n in nodo_ids if n]
        periodo_ids = [p for p in periodo_ids if p]
        movimiento_ids = [m for m in movimiento_ids if m]

        available_nodos = Nodo.objects.filter(
            numero_pc__isnull=False, proyecto=proyecto
        ).select_related('calle_1', 'calle_2')
        all_periodos = list(Periodo.objects.filter(proyecto=proyecto))

        available_fechas = Periodizacion.objects.filter(
            pc__proyecto=proyecto
        ).values_list('fecha', flat=True).distinct().order_by('-fecha')

        mov_qs = PuntoControl.objects.filter(proyecto=proyecto)
        if nodo_ids:
            mov_qs = mov_qs.filter(nodo_id__in=nodo_ids)
        available_movimiento_values = mov_qs.values_list('movimiento', flat=True).distinct().order_by('movimiento')
        movimiento_choices_dict = dict(PuntoControl.Movimiento.choices)
        available_movimientos = [
            {'value': v, 'label': movimiento_choices_dict.get(v, v)}
            for v in available_movimiento_values
        ]

        # Resolve nodo_ids + movimiento_ids to PuntoControl IDs
        pc_qs = PuntoControl.objects.filter(proyecto=proyecto)
        if nodo_ids:
            pc_qs = pc_qs.filter(nodo_id__in=nodo_ids)
        if movimiento_ids:
            pc_qs = pc_qs.filter(movimiento__in=movimiento_ids)
        pc_ids = list(pc_qs.values_list('id', flat=True))

        # Get analysis data
        analisis_data = get_analisis_flujos(
            proyecto_id=proyecto_id,
            pc_ids=pc_ids or None,
            periodo_ids=periodo_ids or None,
            fecha=fecha,
        )

        ranking = get_ranking(analisis_data)
        comparison = get_comparison(analisis_data, all_periodos)
        chart_data = get_chart_data(analisis_data, all_periodos)

        context = {
            'proyecto': proyecto,
            'available_nodos': available_nodos,
            'available_periodos': all_periodos,
            'available_fechas': available_fechas,
            'available_movimientos': available_movimientos,
            'selected_nodos': nodo_ids,
            'selected_periodos': periodo_ids,
            'selected_movimientos': movimiento_ids,
            'selected_fecha': fecha,
            'analisis_data': analisis_data,
            'ranking': ranking,
            'comparison': comparison,
            'comparison_periodos': all_periodos,
            'chart_data_json': json.dumps(chart_data),
            'total_records': len(analisis_data),
        }

        if request.headers.get('HX-Request'):
            return render(request, self.template_container, context)
        return render(request, self.template_full, context)

    @method_decorator(require_http_methods(['POST']))
    def post(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        action = request.POST.get('action') or request.headers.get('X-Action', '')

        if action == 'recalcular':
            created, updated = recalcular_resumenes(proyecto_id)
            return HttpResponse(
                json.dumps({
                    'message': f'Resúmenes recalculados: {created} creados, {updated} actualizados.',
                    'created': created,
                    'updated': updated,
                }),
                content_type='application/json',
                headers={'HX-Trigger': 'resumenes-recalculados'},
            )

        return HttpResponseBadRequest(json.dumps({'error': 'Acción no válida'}))
