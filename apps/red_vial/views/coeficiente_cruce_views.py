from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, QueryDict
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
import json

from apps.red_vial.models import CoeficienteCruce
from apps.red_vial.forms.forms import CoeficienteCruceModelForm
from apps.red_vial.services.coeficiente_cruce_service import (
    get_all_coeficientes_cruce,
    create_coeficiente_cruce,
    update_coeficiente_cruce,
    delete_coeficiente_cruce,
)


@login_required
def coeficientes_cruce_list_view(request):
    items = get_all_coeficientes_cruce()
    form = CoeficienteCruceModelForm()
    context = {'coeficientes': items, 'form': form}

    if request.headers.get('HX-Request'):
        return render(request, 'partials/CoeficientesCruce/coeficientes_cruce_table.html', context)
    return render(request, 'red_vial/CoeficientesCruce/coeficientes_cruce_list.html', context)


@login_required
@require_http_methods(['POST'])
def coeficiente_cruce_create_view(request):
    form = CoeficienteCruceModelForm(request.POST)

    if form.is_valid():
        try:
            item = form.save()
            context = {'item': item, 'coeficiente': item}
            return render(request, 'partials/CoeficientesCruce/coeficiente_cruce_row.html', context)
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}),
                content_type='application/json'
            )

    return render(request, 'partials/CoeficientesCruce/coeficiente_cruce_create.html', {
        'form': form,
    }, status=400)


@login_required
@require_http_methods(['PUT'])
def coeficiente_cruce_update_view(request, item_id):
    try:
        data = QueryDict(request.body)
        item = update_coeficiente_cruce(item_id, data)
        context = {'item': item, 'coeficiente': item}
        response = render(request, 'partials/CoeficientesCruce/coeficiente_cruce_row.html', context)
        response['HX-Trigger'] = f'item-updated:{item.id}'
        return response
    except ValidationError as e:
        return HttpResponseBadRequest(
            json.dumps({'error': str(e)}),
            content_type='application/json'
        )


@login_required
@require_http_methods(['DELETE'])
def coeficiente_cruce_delete_view(request, item_id):
    try:
        delete_coeficiente_cruce(item_id)
        return HttpResponse(status=204)
    except ValidationError as e:
        return HttpResponseBadRequest(
            json.dumps({'error': str(e)}),
            content_type='application/json'
        )
