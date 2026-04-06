from apps.proyectos.services.proyectos_service import *
from apps.proyectos.forms import ProyectoForm
# from apps.mandantes.services.mandantes_service import get_all_mandantes
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required


import base64
from django.core.files.base import ContentFile
from apps.imagenes.services.storage_service import upload_project_image, delete_project_image
from apps.imagenes.utils.image_processor import get_image_from_request

@login_required
def proyectos_view(request):
    proyectos = get_all_proyectos()
    return render(request, "proyectos.html", {
        "proyectos": proyectos,
        "list_title": "Proyectos"
    })


def proyecto_detail_view_RR(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    if request.method == 'GET':
        form = ProyectoForm(instance=proyecto)
        return render(request, 'proyecto_detail.html', {
            'proyecto': proyecto, 
            'form': form})
    else:
        try:
            form = ProyectoForm(request.POST, request.FILES, instance=proyecto)
            if form.is_valid():
                proyecto = form.save(commit=False)
                file = get_image_from_request(request)

                if file:
                    proyecto.image_url = upload_project_image(file)
                else:
                    print("No se recibió ningún archivo de imagen.")

                proyecto.save()
                # form.save()
                return redirect('proyectos')
        except Exception as e:
            return render(request, 'proyecto_detail.html', {'proyecto': proyecto, 'form': form, 'error': str(e)})


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

def proyecto_create_view(request):
   if request.method == 'GET':
       return render(request, 'proyecto_create.html', {
           'form': ProyectoForm
       })
   else:
       try:
           form = ProyectoForm(request.POST)
           new_proyecto = form.save(commit=False)
           new_proyecto.user = request.user
           new_proyecto.save()
           return redirect('proyectos')
       except Exception as e:
           return render(request, 'proyecto_create.html', {
               'form': form,
               'error': str(e)
           })
       

def create_proyecto_view(request):
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



def create_proyecto(request):
    if request.method == 'POST':
        form = ProyectoForm(request.POST)

        if form.is_valid():
            proyecto = form.save(commit=False)

            image_data = request.POST.get("image_file")

            if image_data:
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]

                file = ContentFile(base64.b64decode(imgstr), name=f'upload.{ext}')

                # subir a supabase
                image_url = upload_project_image(file)

                proyecto.image_url = image_url

            proyecto.save()
            return redirect('proyectos')
        

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