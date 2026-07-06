from typing import Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.imagenes.services.storage_service import upload_project_image
from apps.proyectos.models import Proyecto


def get_all_proyectos() -> QuerySet[Proyecto]:
    return Proyecto.objects.all()


def get_active_proyectos() -> QuerySet[Proyecto]:
    return Proyecto.objects.filter(is_completed=False)


def get_completed_proyectos() -> QuerySet[Proyecto]:
    return Proyecto.objects.filter(is_completed=True).order_by("-date_completed")


def get_proyecto_by_id(proyecto_id: str) -> Proyecto:
    return get_object_or_404(Proyecto, id=proyecto_id)


def proyecto_create(data: dict[str, Any]) -> Proyecto:
    return Proyecto.objects.create(**data)


def proyecto_delete(proyecto_id: str) -> None:
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    proyecto.delete()


def create_proyecto(data: dict[str, Any], image_file=None) -> Proyecto:
    image_url = None
    if image_file:
        image_url = upload_project_image(image_file)
    proyecto = Proyecto.objects.create(**data, image_url=image_url)
    return proyecto
