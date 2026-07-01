from typing import Any
from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from apps.red_vial.models import Periodo


# ========== PERIODO SERVICES ==========

def get_all_periodos() -> QuerySet[Periodo]:
    """Obtener todos los períodos"""
    return Periodo.objects.all()


def get_periodo_by_id(periodo_id: str) -> Periodo:
    """Obtener período por ID"""
    return get_object_or_404(Periodo, id=periodo_id)


def get_periodo_by_codigo(codigo: str) -> Periodo:
    """Obtener período por código (PM-L, PT-L, etc.)"""
    return get_object_or_404(Periodo, codigo=codigo)


def periodo_create(data: dict[str, Any]) -> Periodo:
    """Crear un nuevo período"""
    return Periodo.objects.create(**data)


def periodo_update(periodo_id: str, data: dict[str, Any]) -> Periodo:
    """Actualizar un período"""
    periodo = get_object_or_404(Periodo, id=periodo_id)
    for key, value in data.items():
        setattr(periodo, key, value)
    periodo.save()
    return periodo


def periodo_delete(periodo_id: str) -> None:
    """Eliminar un período"""
    periodo = get_object_or_404(Periodo, id=periodo_id)
    periodo.delete()
