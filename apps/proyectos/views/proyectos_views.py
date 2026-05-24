from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from apps.proyectos.services.proyectos_service import *
from apps.proyectos.forms import ProyectoForm

from apps.imagenes.services.storage_service import upload_project_image, delete_project_image
from apps.imagenes.utils.image_processor import get_image_from_request

@login_required
def proyectos_view(request):
    proyectos = get_all_proyectos()
    return render(request, "proyectos.html", {
        "proyectos": proyectos,
        "list_title": "Proyectos"
    })


@login_required
def proyecto_detail_view(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)

    if request.method == 'GET':
        form = ProyectoForm(instance=proyecto)
        return render(request, 'proyecto_detail.html', {
            'proyecto': proyecto,
            'form': form
        })

    try:
        form = ProyectoForm(request.POST, request.FILES, instance=proyecto)

        if not form.is_valid():
            raise ValueError("Formulario inválido")

        proyecto = form.save(commit=False)

        file = get_image_from_request(request)

        # 🔥 SOLO actualizar imagen si viene una nueva
        if file:
            if proyecto.image_url:
                delete_project_image(proyecto.image_url)
            proyecto.image_url = upload_project_image(file)

        # 👇 si no hay file, NO tocamos image_url

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

# ========== PROJECT SECTIONS ==========






