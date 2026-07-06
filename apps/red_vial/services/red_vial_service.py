from typing import Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404

from apps.red_vial.models import Coeficiente_Cruce


def get_all_coeficientes() -> QuerySet[Coeficiente_Cruce]:
    return Coeficiente_Cruce.objects.all()


def get_coeficiente_by_id(coeficiente_id: str) -> Coeficiente_Cruce:
    return get_object_or_404(Coeficiente_Cruce, id=coeficiente_id)


def get_coeficiente_by_nomenclatura(nomenclatura: str) -> Coeficiente_Cruce:
    return get_object_or_404(Coeficiente_Cruce, nomenclatura=nomenclatura)


def get_coeficientes_standard() -> QuerySet[Coeficiente_Cruce]:
    return Coeficiente_Cruce.objects.filter(is_standard=True)


def coeficiente_create(data: dict[str, Any]) -> Coeficiente_Cruce:
    return Coeficiente_Cruce.objects.create(**data)


def coeficiente_update(coeficiente_id: str, data: dict[str, Any]) -> Coeficiente_Cruce:
    coeficiente = get_object_or_404(Coeficiente_Cruce, id=coeficiente_id)
    for key, value in data.items():
        setattr(coeficiente, key, value)
    coeficiente.save()
    return coeficiente


def coeficiente_delete(coeficiente_id: str) -> None:
    coeficiente = get_object_or_404(Coeficiente_Cruce, id=coeficiente_id)
    coeficiente.delete()
