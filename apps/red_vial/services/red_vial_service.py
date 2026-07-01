from typing import Any

from django.db.models import QuerySet
from django.shortcuts import get_object_or_404
from apps.red_vial.models import (
    Calle,
    Nodo,
    Arco,
    Regulacion,
    Coeficiente_Cruce,
)
from apps.proyectos.models import Proyecto




# ========== REGULACION SERVICES ==========

def get_all_regulaciones() -> QuerySet[Regulacion]:
    """Obtener todos los tipos de regulación"""
    return Regulacion.objects.all()


def get_regulacion_by_id(regulacion_id: str) -> Regulacion:
    """Obtener regulación por ID"""
    return get_object_or_404(Regulacion, id=regulacion_id)


def get_regulacion_by_codigo(codigo: str) -> Regulacion:
    """Obtener regulación por código (DIR, DER, IZQ)"""
    return get_object_or_404(Regulacion, codigo=codigo)


def regulacion_create(data: dict[str, Any]) -> Regulacion:
    """Crear un nuevo tipo de regulación"""
    return Regulacion.objects.create(**data)


def regulacion_update(regulacion_id: str, data: dict[str, Any]) -> Regulacion:
    """Actualizar una regulación"""
    regulacion = get_object_or_404(Regulacion, id=regulacion_id)
    for key, value in data.items():
        setattr(regulacion, key, value)
    regulacion.save()
    return regulacion


def regulacion_delete(regulacion_id: str) -> None:
    """Eliminar una regulación"""
    regulacion = get_object_or_404(Regulacion, id=regulacion_id)
    regulacion.delete()


# ========== COEFICIENTE CRUCE SERVICES ==========

def get_all_coeficientes() -> QuerySet[Coeficiente_Cruce]:
    """Obtener todos los coeficientes de cruce"""
    return Coeficiente_Cruce.objects.all()


def get_coeficiente_by_id(coeficiente_id: str) -> Coeficiente_Cruce:
    """Obtener coeficiente por ID"""
    return get_object_or_404(Coeficiente_Cruce, id=coeficiente_id)


def get_coeficiente_by_nomenclatura(nomenclatura: str) -> Coeficiente_Cruce:
    """Obtener coeficiente por nomenclatura (VL, TXC, etc.)"""
    return get_object_or_404(Coeficiente_Cruce, nomenclatura=nomenclatura)


def get_coeficientes_standard() -> QuerySet[Coeficiente_Cruce]:
    """Obtener coeficientes estándar"""
    return Coeficiente_Cruce.objects.filter(is_standard=True)


def coeficiente_create(data: dict[str, Any]) -> Coeficiente_Cruce:
    """Crear un nuevo coeficiente"""
    return Coeficiente_Cruce.objects.create(**data)


def coeficiente_update(coeficiente_id: str, data: dict[str, Any]) -> Coeficiente_Cruce:
    """Actualizar un coeficiente"""
    coeficiente = get_object_or_404(Coeficiente_Cruce, id=coeficiente_id)
    for key, value in data.items():
        setattr(coeficiente, key, value)
    coeficiente.save()
    return coeficiente


def coeficiente_delete(coeficiente_id: str) -> None:
    """Eliminar un coeficiente"""
    coeficiente = get_object_or_404(Coeficiente_Cruce, id=coeficiente_id)
    coeficiente.delete()


# ========== IMPORT/EXPORT SERVICES ==========

def import_calles_from_excel(proyecto_id: str, calles_data: list[dict[str, Any]]) -> list[Calle]:
    """Importar calles desde datos de Excel"""
    calles_creadas = []
    for data in calles_data:
        data['proyecto_id'] = proyecto_id
        calle = Calle.objects.create(**data)
        calles_creadas.append(calle)
    return calles_creadas


def import_nodos_from_excel(proyecto_id: str, nodos_data: list[dict[str, Any]], calles_mapping: dict[str | int, str]) -> list[Nodo]:
    """Importar nodos desde datos de Excel"""
    nodos_creados = []
    for data in nodos_data:
        data['proyecto_id'] = proyecto_id
        # Mapear IDs de calles si es necesario
        if 'calle_1_numero' in data:
            data['calle_1_id'] = calles_mapping.get(data.pop('calle_1_numero'))
        if 'calle_2_numero' in data:
            data['calle_2_id'] = calles_mapping.get(data.pop('calle_2_numero'))
        nodo = Nodo.objects.create(**data)
        nodos_creados.append(nodo)
    return nodos_creados


def import_arcos_from_excel(proyecto_id: str, arcos_data: list[dict[str, Any]], nodos_mapping: dict[str | int, str]) -> list[Arco]:
    """Importar arcos desde datos de Excel"""
    arcos_creados = []
    for data in arcos_data:
        data['proyecto_id'] = proyecto_id
        # Mapear IDs de nodos
        if 'nodo_origen_numero' in data:
            data['nodo_origen_id'] = nodos_mapping.get(data.pop('nodo_origen_numero'))
        if 'nodo_destino_numero' in data:
            data['nodo_destino_id'] = nodos_mapping.get(data.pop('nodo_destino_numero'))
        arco = Arco.objects.create(**data)
        arcos_creados.append(arco)
    return arcos_creados
