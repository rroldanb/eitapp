from django.views import View
from apps.red_vial.models import Calle
from apps.red_vial.forms.forms import CalleForm
from apps.red_vial.services.calle_service import (
    get_calles_by_proyecto,
    create_calle,
    update_calle,
    delete_calle,
    bulk_update_calles
)
from .generic_views import GenericListView, GenericCreateView, GenericUpdateView, GenericDeleteView, GenericBulkUpdateView


# ========== CALLE VIEWS ==========

class CallesListView(GenericListView):
    """Lista de calles de un proyecto con ordenamiento."""
    model = Calle
    service_get_function = get_calles_by_proyecto
    sort_fields = ['numero', 'nombre', 'nodos']
    default_sort = 'numero'
    partial_template = 'partials/Calles/calles_table.html'
    full_template = 'red_vial/Calles/calles_list.html'
    context_items_key = 'calles'


class CallesCreateView(GenericCreateView):
    """Crear una nueva calle."""
    model = Calle
    form_class = CalleForm
    service_create_function = create_calle
    row_template = 'partials/Calles/calle_row.html'
    form_template = 'partials/Calles/calle_create.html'


class CallesUpdateView(GenericUpdateView):
    """Actualizar una calle."""
    model = Calle
    service_update_function = update_calle
    row_template = 'partials/Calles/calle_row.html'


class CallesDeleteView(GenericDeleteView):
    """Eliminar una calle."""
    model = Calle
    service_delete_function = delete_calle


class CallesBulkUpdateView(GenericBulkUpdateView):
    """Actualizar múltiples calles en lote."""
    service_bulk_update = bulk_update_calles

