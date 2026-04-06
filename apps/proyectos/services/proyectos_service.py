from apps.proyectos.models import Proyecto
from apps.imagenes.services.storage_service import upload_project_image

def get_all_proyectos():
    return Proyecto.objects.all()

def get_proyecto_by_id(proyecto_id):
    return Proyecto.objects.get(id=proyecto_id)

def proyecto_create(data):
    return Proyecto.objects.create(**data)

def proyecto_delete(proyecto_id):
    proyecto = Proyecto.objects.get(id=proyecto_id)
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