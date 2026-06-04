import json
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods

from apps.red_vial.models import CoeficienteCruce
from apps.proyectos.models import Proyecto
from apps.red_vial.forms.coeficiente_cruce_form import CoeficienteCruceModelForm
from apps.red_vial.services.coeficiente_cruce_service import (
    get_all_coeficientes_cruce, create_coeficiente_cruce,
    update_coeficiente_cruce, delete_coeficiente_cruce,
)


@method_decorator(login_required, name='dispatch')
class CoeficientesCruceListView(View):
    sort_fields = ['nomenclatura', 'tipo_transporte', 'coeficiente', 'proyecto']
    default_sort = 'nomenclatura'

    def get(self, request, proyecto_id):
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        sort_by = request.GET.get('sort_by', self.default_sort)
        sort_order = request.GET.get('sort_order', 'asc')
        if sort_by not in self.sort_fields:
            sort_by = self.default_sort
        if sort_order not in ['asc', 'desc']:
            sort_order = 'asc'
        items = get_all_coeficientes_cruce(sort_by=sort_by, order=sort_order)
        form = CoeficienteCruceModelForm()
        available_projects = Proyecto.objects.only('id', 'title').order_by('title')
        standard_coeficientes = CoeficienteCruce.objects.filter(
            proyecto__isnull=True
        ).values('nomenclatura', 'tipo_transporte').order_by('nomenclatura')
        context = {
            'proyecto': proyecto,
            'coeficientes': items,
            'coeficientes_count': items.count(),
            'form': form,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'available_projects': available_projects,
            'standard_coeficientes': list(standard_coeficientes),
        }
        if request.headers.get('HX-Request'):
            return render(request, 'partials/CoeficientesCruce/coeficientes_cruce_table.html', context)
        return render(request, 'red_vial/coeficientes_cruce_list.html', context)


@method_decorator(login_required, name='dispatch')
class CoeficienteCruceCreateView(View):
    @method_decorator(require_http_methods(['POST']))
    def post(self, request):
        form = CoeficienteCruceModelForm(request.POST)
        if form.is_valid():
            try:
                item = create_coeficiente_cruce(form.cleaned_data)
                proys = Proyecto.objects.only('id', 'title').order_by('title')
                ctx = {'item': item, 'coeficiente': item, 'available_projects': proys}
                return render(request, 'partials/CoeficientesCruce/coeficiente_cruce_row.html', ctx)
            except ValidationError as e:
                return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type='application/json')
        proys = Proyecto.objects.only('id', 'title').order_by('title')
        standards = list(CoeficienteCruce.objects.filter(proyecto__isnull=True).values('nomenclatura', 'tipo_transporte').order_by('nomenclatura'))
        ctx = {'form': form, 'available_projects': proys, 'standard_coeficientes': standards}
        return render(request, 'partials/CoeficientesCruce/coeficiente_cruce_create.html', ctx, status=400)


@method_decorator(login_required, name='dispatch')
class CoeficienteCruceUpdateView(View):
    @method_decorator(require_http_methods(['PUT']))
    def put(self, request, item_id):
        from django.http import QueryDict
        try:
            data = QueryDict(request.body)
            item = update_coeficiente_cruce(item_id, data)
            ctx = {'item': item, 'coeficiente': item, 'available_projects': Proyecto.objects.only('id', 'title').order_by('title')}
            response = render(request, 'partials/CoeficientesCruce/coeficiente_cruce_row.html', ctx)
            response['HX-Trigger'] = f'item-updated:{item.id}'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type='application/json')


@method_decorator(login_required, name='dispatch')
class CoeficienteCruceDeleteView(View):
    @method_decorator(require_http_methods(['DELETE']))
    def delete(self, request, item_id):
        try:
            delete_coeficiente_cruce(item_id)
            return HttpResponse('', status=200)
        except ValidationError as e:
            return HttpResponseBadRequest(json.dumps({'error': str(e)}), content_type='application/json')
