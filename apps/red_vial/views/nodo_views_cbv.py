from apps.red_vial.models import Nodo
from apps.red_vial.forms.nodo_form import NodoForm
from apps.red_vial.services.nodo_service import (
    get_nodos_by_proyecto,
    create_nodo,
    update_nodo,
    delete_nodo,
    bulk_update_nodos,
)
from .generic_views import (
    GenericListView,
    GenericCreateView,
    GenericUpdateView,
    GenericDeleteView,
    GenericBulkUpdateView,
)


class NodosListView(GenericListView):
    model = Nodo
    service_get_function = get_nodos_by_proyecto
    sort_fields = ['numero', 'calle_1', 'calle_2', 'is_pc']
    default_sort = 'numero'
    partial_template = 'partials/Nodos/nodos_table.html'
    full_template = 'red_vial/nodos_list.html'
    context_items_key = 'nodos'


class NodosCreateView(GenericCreateView):
    model = Nodo
    form_class = NodoForm
    service_create_function = create_nodo
    row_template = 'partials/Nodos/nodo_row.html'
    form_template = 'partials/Nodos/nodo_create.html'


class NodosUpdateView(GenericUpdateView):
    model = Nodo
    service_update_function = update_nodo
    row_template = 'partials/Nodos/nodo_row.html'


class NodosDeleteView(GenericDeleteView):
    model = Nodo
    service_delete_function = delete_nodo


class NodosBulkUpdateView(GenericBulkUpdateView):
    service_bulk_update = bulk_update_nodos
