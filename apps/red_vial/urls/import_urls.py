from django.urls import path
from ..views.import_views import (
    import_start,
    import_upload,
    import_back_step1,
    import_goto_selection,
    import_validate,
    import_execute,
    import_cancel,
    import_project_select,
)

urlpatterns = [
    path("importar/", import_project_select, name="import_project_select"),
    path("proyecto/<uuid:proyecto_id>/importar/", import_start, name="import_start"),
    path("proyecto/<uuid:proyecto_id>/importar/upload/", import_upload, name="import_upload"),
    path("proyecto/<uuid:proyecto_id>/importar/back-step1/", import_back_step1, name="import_back_step1"),
    path("proyecto/<uuid:proyecto_id>/importar/goto-selection/", import_goto_selection, name="import_goto_selection"),
    path("proyecto/<uuid:proyecto_id>/importar/validate/", import_validate, name="import_validate"),
    path("proyecto/<uuid:proyecto_id>/importar/execute/", import_execute, name="import_execute"),
    path("proyecto/<uuid:proyecto_id>/importar/cancel/", import_cancel, name="import_cancel"),
]
