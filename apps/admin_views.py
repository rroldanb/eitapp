from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.utils.decorators import method_decorator
from django.shortcuts import render
from .common.utils.excel_utils import generar_plantilla_bytes


@staff_member_required
def descargar_plantilla(request):
    buf = generar_plantilla_bytes()
    response = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="plantilla_importacion_eitapp.xlsx"'
    return response
