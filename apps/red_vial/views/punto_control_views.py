from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_http_methods
from django.core.exceptions import ValidationError
import json
import inspect

from apps.red_vial.models import PuntoControl
from apps.red_vial.forms.punto_control_form import PuntoControlForm
from apps.red_vial.services.punto_control_service import (
    get_puntos_control_by_proyecto,
    create_punto_control,
    update_punto_control,
    delete_punto_control,
)
from .generic_views import GenericListView, GenericCreateView, GenericUpdateView, GenericDeleteView
from apps.proyectos.models import Proyecto



class PuntosControlListView(GenericListView):
    model = PuntoControl
    service_get_function = get_puntos_control_by_proyecto
    sort_fields = ['nombre', 'nodo', 'movimiento', 'viraje', 'arco_entrada', 'arco_salida']
    default_sort = 'nombre'
    partial_template = 'partials/PuntosControl/puntos_control_table.html'
    full_template = 'red_vial/puntos_control_list.html'
    context_items_key = 'puntos_control'
    form_class = PuntoControlForm
    
    # @method_decorator(login_required)
    # def get(self, request, proyecto_id=None):
    #     resolver_kwargs = getattr(request, 'resolver_match', None)
    #     if resolver_kwargs:
    #         proyecto_id = resolver_kwargs.kwargs.get('proyecto_id', proyecto_id)

    #     proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    #     sort_by = request.GET.get('sort_by', self.default_sort)
    #     sort_order = request.GET.get('sort_order', 'asc')

    #     if sort_by not in self.sort_fields:
    #         sort_by = self.default_sort
    #     if sort_order not in ['asc', 'desc']:
    #         sort_order = 'asc'

    #     try:
    #         sig = inspect.signature(self.__class__.service_get_function)
    #         accepted = set(sig.parameters.keys())
    #     except (ValueError, TypeError):
    #         accepted = set()

    #     call_kwargs = {'proyecto_id': proyecto_id}
    #     if 'sort_by' in accepted:
    #         call_kwargs['sort_by'] = sort_by
    #     if 'order' in accepted:
    #         call_kwargs['order'] = sort_order

    #     items = self.__class__.service_get_function(**call_kwargs)

    #     form = PuntoControlForm(proyecto=proyecto)

    #     context = {
    #         'proyecto': proyecto,
    #         self.context_items_key: items,
    #         'sort_by': sort_by,
    #         'sort_order': sort_order,
    #         'sort_fields': self.sort_fields,
    #         'form': form,
    #     }

    #     if request.headers.get('HX-Request'):
    #         return render(request, self.partial_template, context)
    #     return render(request, self.full_template, context)


class PuntosControlCreateView(GenericCreateView):
    model = PuntoControl
    form_class = PuntoControlForm
    service_create_function = create_punto_control
    row_template = 'partials/PuntosControl/punto_control_row.html'
    form_template = 'partials/PuntosControl/punto_control_create.html'
    form_class = PuntoControlForm

    # @method_decorator(login_required)
    # @method_decorator(require_http_methods(['POST']))
    # def post(self, request, proyecto_id):

    #     proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    #     form = self.form_class(request.POST, proyecto=proyecto)

    #     if form.is_valid():
    #         try:
    #             service_func = self.__class__.service_create_function
    #             item = service_func(proyecto, form.cleaned_data)
    #             singular = self.model._meta.model_name if self.model is not None else 'item'
    #             context = {'item': item, 'proyecto': proyecto, singular: item}
    #             print(f"Context for {singular} creation:", context)  # Debug log
    #             return render(request, self.row_template, context)
    #         except ValidationError as e:
    #             return HttpResponseBadRequest(
    #                 json.dumps({'error': str(e)}),
    #                 content_type='application/json'
    #             )

    #     return render(request, self.form_template, {
    #         'proyecto': proyecto,
    #         'form': form,
    #     }, status=400)


class PuntosControlUpdateView(GenericUpdateView):
    model = PuntoControl
    service_update_function = update_punto_control
    row_template = 'partials/PuntosControl/punto_control_row.html'
    form_class = PuntoControlForm


class PuntosControlDeleteView(GenericDeleteView):
    model = PuntoControl
    service_delete_function = delete_punto_control
