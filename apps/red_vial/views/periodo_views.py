from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest, JsonResponse, HttpResponse
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.views import View
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import json
import inspect

from apps.red_vial.models import Periodo
from apps.red_vial.forms.trafico_forms import PeriodoForm
from apps.red_vial.services.trafico_service import periodo_delete
from apps.proyectos.models import Proyecto


@method_decorator(login_required, name='dispatch')
class PeriodoListView(View):
    template_full = 'red_vial/Periodo/periodo_list.html'
    template_table = 'partials/Periodo/periodo_table.html'

    def get(self, request, proyecto_id):
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        periodos = Periodo.objects.filter(proyecto=proyecto).order_by('codigo')

        form = PeriodoForm(proyecto=proyecto)

        context = {
            'proyecto': proyecto,
            'periodos': periodos,
            'form': form,
        }

        if request.headers.get('HX-Request'):
            return render(request, self.template_table, context)
        return render(request, self.template_full, context)


@method_decorator(login_required, name='dispatch')
@method_decorator(require_http_methods(['POST']), name='dispatch')
class PeriodoCreateView(View):
    def post(self, request, proyecto_id):
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        form = PeriodoForm(request.POST, proyecto=proyecto)

        if form.is_valid():
            try:
                periodo = form.save()
                form = PeriodoForm(proyecto=proyecto)
                context = {
                    'item': periodo,
                    'proyecto': proyecto,
                    'form': form,
                    'periodo': periodo,
                }
                return render(request, 'partials/Periodo/periodo_row.html', context)
            except IntegrityError:
                form.add_error('codigo', 'Ya existe un período con ese código en este proyecto.')

        context = {
            'proyecto': proyecto,
            'form': form,
        }
        return render(request, 'partials/Periodo/periodo_create.html', context, status=400)


@method_decorator(login_required, name='dispatch')
@method_decorator(require_http_methods(['PUT']), name='dispatch')
class PeriodoUpdateView(View):
    def put(self, request, item_id):
        periodo = get_object_or_404(Periodo, id=item_id)
        proyecto = periodo.proyecto

        from django.http import QueryDict
        data = QueryDict(request.body).dict()

        form = PeriodoForm(data, instance=periodo, proyecto=proyecto)
        if form.is_valid():
            try:
                periodo = form.save()
                context = {
                    'item': periodo,
                    'proyecto': proyecto,
                    'form': PeriodoForm(proyecto=proyecto),
                    'periodo': periodo,
                }
                response = render(request, 'partials/Periodo/periodo_row.html', context)
                response['HX-Trigger'] = f'periodo-updated:{periodo.id}'
                return response
            except IntegrityError:
                form.add_error('codigo', 'Ya existe un período con ese código en este proyecto.')

        return HttpResponseBadRequest(
            json.dumps({'error': str(form.errors)}),
            content_type='application/json',
        )


@method_decorator(login_required, name='dispatch')
@method_decorator(require_http_methods(['DELETE']), name='dispatch')
class PeriodoDeleteView(View):
    def delete(self, request, item_id):
        try:
            periodo_delete(item_id)
            return HttpResponse(status=204)
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}),
                content_type='application/json',
            )
