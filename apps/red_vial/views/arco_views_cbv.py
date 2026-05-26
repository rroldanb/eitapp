from apps.red_vial.models import Arco
from apps.red_vial.forms.forms import ArcoForm
from apps.red_vial.services.arco_service import (
    get_arcos_by_proyecto,
    create_arco,
    update_arco,
    delete_arco,
    bulk_update_arcos,
)
from .generic_views import (
    GenericListView,
    GenericCreateView,
    GenericUpdateView,
    GenericDeleteView,
    GenericBulkUpdateView,
)


class ArcosListView(GenericListView):
    model = Arco
    service_get_function = get_arcos_by_proyecto
    sort_fields = [ 'codigo_arco','origen', 'destino', 'longitud']
    default_sort = 'codigo_arco'
    partial_template = 'partials/Arcos/arcos_table.html'
    full_template = 'red_vial/Arcos/arcos_list.html'
    context_items_key = 'arcos'


class ArcosCreateView(GenericCreateView):
    model = Arco
    form_class = ArcoForm
    service_create_function = create_arco
    row_template = 'partials/Arcos/arco_row.html'
    form_template = 'partials/Arcos/arco_create.html'


class ArcosUpdateView(GenericUpdateView):
    model = Arco
    service_update_function = update_arco
    row_template = 'partials/Arcos/arco_row.html'


class ArcosDeleteView(GenericDeleteView):
    model = Arco
    service_delete_function = delete_arco


class ArcosBulkUpdateView(GenericBulkUpdateView):
    service_bulk_update = bulk_update_arcos
