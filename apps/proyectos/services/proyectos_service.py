from django.shortcuts import get_object_or_404
from apps.proyectos.models import Proyecto
from apps.imagenes.services.storage_service import upload_project_image

def get_all_proyectos():
    return Proyecto.objects.all()

def get_active_proyectos():
    return Proyecto.objects.filter(is_completed=False)

def get_completed_proyectos():
    return Proyecto.objects.filter(is_completed=True).order_by('-date_completed')

def get_proyecto_by_id(proyecto_id):
    return get_object_or_404(Proyecto, id=proyecto_id)

def proyecto_create(data):
    return Proyecto.objects.create(**data)

def proyecto_delete(proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    proyecto.delete()


def create_proyecto(data, image_file=None):

    image_url = None

    if image_file:
        image_url = upload_project_image(image_file)

    proyecto = Proyecto.objects.create(
        **data,
        image_url=image_url
    )

    return proyecto