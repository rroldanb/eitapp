import json

from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods

from apps.red_vial.models import Regulacion
from apps.red_vial.forms.forms import RegulacionForm
from apps.red_vial.services.regulacion_service import (
    get_all_regulaciones,
    create_regulacion,
    update_regulacion,
    delete_regulacion,
)


class RegulacionesListView(View):
    sort_fields = ['codigo', 'descripcion']
    default_sort = 'codigo'

    @method_decorator(login_required)
    def get(self, request):
        sort_by = request.GET.get('sort_by', self.default_sort)
        sort_order = request.GET.get('sort_order', 'asc')

        if sort_by not in self.sort_fields:
            sort_by = self.default_sort
        if sort_order not in ['asc', 'desc']:
            sort_order = 'asc'

        regulaciones = get_all_regulaciones(sort_by=sort_by, order=sort_order)

        context = {
            'regulaciones': regulaciones,
            'sort_by': sort_by,
            'sort_order': sort_order,
        }

        if request.headers.get('HX-Request'):
            return render(request, 'partials/Regulaciones/regulaciones_table.html', context)
        return render(request, 'red_vial/Regulaciones/regulaciones_list.html', context)


class RegulacionCreateView(View):

    @method_decorator(login_required)
    @method_decorator(require_http_methods(['POST']))
    def post(self, request):
        form = RegulacionForm(request.POST)

        if form.is_valid():
            try:
                item = create_regulacion(form.cleaned_data)
                return render(request, 'partials/Regulaciones/regulacion_row.html', {'item': item, 'regulacion': item})
            except ValidationError as e:
                return HttpResponseBadRequest(
                    json.dumps({'error': str(e)}),
                    content_type='application/json'
                )

        return render(request, 'partials/Regulaciones/regulacion_create.html', {'form': form}, status=400)


class RegulacionUpdateView(View):

    @method_decorator(login_required)
    @method_decorator(require_http_methods(['PUT']))
    def put(self, request, item_id):
        from django.http import QueryDict

        try:
            data = QueryDict(request.body)
            item = update_regulacion(item_id, data)
            context = {'item': item, 'regulacion': item}
            response = render(request, 'partials/Regulaciones/regulacion_row.html', context)
            response['HX-Trigger'] = f'item-updated:{item.id}'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}),
                content_type='application/json'
            )


class RegulacionDeleteView(View):

    @method_decorator(login_required)
    @method_decorator(require_http_methods(['DELETE']))
    def delete(self, request, item_id):
        try:
            delete_regulacion(item_id)
            return HttpResponse(status=204)
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}),
                content_type='application/json'
            )
