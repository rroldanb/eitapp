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
    sort_fields = ['nombre', 'nodo', 'movimiento', 'viraje', 'arco_entrada', 'arco_salida','numero_pistas']
    default_sort = 'nombre'
    partial_template = 'partials/PuntosControl/puntos_control_table.html'
    full_template = 'red_vial/puntos_control_list.html'
    context_items_key = 'puntos_control'
    form_class = PuntoControlForm
    


class PuntosControlCreateView(GenericCreateView):
    model = PuntoControl
    form_class = PuntoControlForm
    service_create_function = create_punto_control
    row_template = 'partials/PuntosControl/punto_control_row.html'
    form_template = 'partials/PuntosControl/punto_control_create.html'
    form_class = PuntoControlForm




class PuntosControlUpdateView(GenericUpdateView):
    model = PuntoControl
    service_update_function = update_punto_control
    row_template = 'partials/PuntosControl/punto_control_row.html'
    form_class = PuntoControlForm


class PuntosControlDeleteView(GenericDeleteView):
    model = PuntoControl
    service_delete_function = delete_punto_control
