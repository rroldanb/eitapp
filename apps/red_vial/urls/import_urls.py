from django.urls import path
from ..views.import_views import (
    import_landing,
    import_start,
    import_upload,
    import_configure,
    import_back_config,
    import_back_upload,
    import_goto_selection,
    import_validate,
    import_execute,
    import_cancel,
)

urlpatterns = [
    path("importar/", import_landing, name="import_landing"),
    path("importar/upload/", import_upload, name="import_upload"),
    path("importar/configure/", import_configure, name="import_configure"),
    path("proyecto/<uuid:proyecto_id>/importar/", import_start, name="import_start"),
    path("proyecto/<uuid:proyecto_id>/importar/goto-selection/", import_goto_selection, name="import_goto_selection"),
    path("proyecto/<uuid:proyecto_id>/importar/back-config/", import_back_config, name="import_back_config"),
    path("proyecto/<uuid:proyecto_id>/importar/back-upload/", import_back_upload, name="import_back_step1"),
    path("proyecto/<uuid:proyecto_id>/importar/validate/", import_validate, name="import_validate"),
    path("proyecto/<uuid:proyecto_id>/importar/execute/", import_execute, name="import_execute"),
    path("proyecto/<uuid:proyecto_id>/importar/cancel/", import_cancel, name="import_cancel"),
]
