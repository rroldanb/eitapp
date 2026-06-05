from io import BytesIO
import zipfile

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone
from django.http import HttpResponse
from django.contrib import messages

from apps.proyectos.services.proyectos_service import *
from apps.proyectos.forms import ProyectoForm
from apps.proyectos.models import Proyecto

from apps.imagenes.services.storage_service import upload_project_image, delete_project_image
from apps.imagenes.utils.image_processor import get_image_from_request
from apps.red_vial.services.generador_dat import DatGenerator, generar_parametros_arco, generar_fases_semaforicas
from apps.red_vial.models import Periodo

@login_required
def proyectos_view(request):
    active_proyectos = get_active_proyectos()
    completed_proyectos = get_completed_proyectos()
    return render(request, "proyectos.html", {
        "active_proyectos": active_proyectos,
        "completed_proyectos": completed_proyectos,
        "list_title": "Proyectos"
    })


@login_required
def proyecto_detail_view(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    if request.method == 'GET':
        form = ProyectoForm(instance=proyecto)
        pendientes = DatGenerator(proyecto).validate()
        periodos = Periodo.objects.filter(proyecto=proyecto)
        return render(request, 'proyecto_detail.html', {
            'proyecto': proyecto,
            'form': form,
            'pendientes': pendientes,
            'periodos': periodos,
        })

    try:
        form = ProyectoForm(request.POST, request.FILES, instance=proyecto)

        if not form.is_valid():
            raise ValueError("Formulario inválido")

        proyecto = form.save(commit=False)

        file = get_image_from_request(request)

        if file:
            if proyecto.image_url:
                delete_project_image(proyecto.image_url)
            proyecto.image_url = upload_project_image(file)
        elif request.POST.get('image_triggered') == 'delete':
            if proyecto.image_url:
                delete_project_image(proyecto.image_url)
            proyecto.image_url = None

        proyecto.save()

        return redirect('proyectos')

    except Exception as e:
        return render(request, 'proyecto_detail.html', {
            'proyecto': proyecto,
            'form': form,
            'error': str(e)
        })

@login_required
def proyecto_create_view(request):
    if request.method == "POST":
        form = ProyectoForm(request.POST, request.FILES)

        try:
            if not form.is_valid():
                raise ValueError("Formulario inválido")

            proyecto = form.save(commit=False)
            proyecto.user = request.user

            file = get_image_from_request(request)

            if file:
                proyecto.image_url = upload_project_image(file)

            proyecto.save()

            return redirect("proyectos")

        except Exception as e:
            return render(request, "proyecto_create.html", {
                "form": form,
                "error": str(e)
            })

    return render(request, "proyecto_create.html", {
        "form": ProyectoForm()
    })


@login_required
@require_POST
def proyecto_finalizar_view(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    proyecto.is_completed = True
    proyecto.date_completed = timezone.now()
    proyecto.save()
    return redirect('proyecto_detail', proyecto_id=proyecto_id)


@login_required
@require_POST
def proyecto_reactivar_view(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    proyecto.is_completed = False
    proyecto.date_completed = None
    proyecto.save()
    return redirect('proyecto_detail', proyecto_id=proyecto_id)


@login_required
@require_POST
def proyecto_delete_image_view(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    try:
        if proyecto.image_url:
            delete_project_image(proyecto.image_url)
        proyecto.image_url = None
        proyecto.save()
    except Exception as e:
        pass
    return redirect('proyecto_detail', proyecto_id=proyecto_id)


@login_required
def proyecto_delete_view(request, proyecto_id):
    try:
        proyecto_delete(proyecto_id)
        return redirect('proyectos')
    except Exception as e:
        return render(request, 'proyectos.html', {
            'error': str(e),
            'proyectos': get_all_proyectos(),
            'list_title': "Proyectos"
        })


@login_required
def proyecto_resumen_view(request, proyecto_id):
    """Vista de resumen de Red Vial del proyecto"""
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    calles = proyecto.calles.all()
    nodos = proyecto.nodos.all().select_related('calle_1', 'calle_2')
    arcos = proyecto.arcos.all().select_related('nodo_origen', 'nodo_destino')

    return render(request, 'proyecto_resumen.html', {
        'proyecto': proyecto,
        'calles': calles,
        'nodos': nodos,
        'arcos': arcos,
        'active_section': 'resumen'
    })

@login_required
@require_GET
def proyecto_generar_dat_view(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    periodo_id = request.GET.get('periodo')

    gen = DatGenerator(proyecto, periodo_id=periodo_id if periodo_id != 'all' else None)
    errors = gen.validate()
    if errors:
        return redirect(f'{request.META.get("HTTP_REFERER", "/")}?error_dat=1')

    if periodo_id == 'all':
        files = gen.generate_all_periods()
        if len(files) == 1:
            codigo, content = next(iter(files.items()))
            filename = f'{proyecto.title.replace(" ", "_")}_{codigo}.dat'
            response = HttpResponse(content, content_type='text/plain; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response

        buf = BytesIO()
        with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
            for codigo, content in files.items():
                zf.writestr(f'{proyecto.title.replace(" ", "_")}_{codigo}.dat', content)
        buf.seek(0)
        filename = f'{proyecto.title.replace(" ", "_")}_todos_periodos.zip'
        response = HttpResponse(buf.getvalue(), content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    content, _ = gen.generate()
    periodo = Periodo.objects.filter(id=periodo_id, proyecto=proyecto).first() if periodo_id else None
    suffix = f'_{periodo.codigo}' if periodo else ''
    filename = f'{proyecto.title.replace(" ", "_")}{suffix}.dat'
    response = HttpResponse(content, content_type='text/plain; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@login_required
@require_POST
def proyecto_generar_parametros_arco_view(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    count = generar_parametros_arco(proyecto)
    messages.success(request, f'Se crearon {count} parámetros de arco.')
    return redirect('parametros_arco_list', proyecto_id=proyecto_id)


@login_required
@require_POST
def proyecto_generar_fases_semaforicas_view(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    count = generar_fases_semaforicas(proyecto)
    messages.success(request, f'Se crearon {count} fases semafóricas.')
    return redirect('fases_semaforicas_list', proyecto_id=proyecto_id)


# ========== PROJECT SECTIONS ==========






