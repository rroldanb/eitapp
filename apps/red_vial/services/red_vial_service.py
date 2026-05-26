from apps.red_vial.models import (
    Calle,
    Nodo,
    Arco,
    Regulacion,
    NodoMovimiento,
    Coeficiente_Cruce,
)
from apps.proyectos.models import Proyecto




# ========== REGULACION SERVICES ==========

def get_all_regulaciones():
    """Obtener todos los tipos de regulación"""
    return Regulacion.objects.all()


def get_regulacion_by_id(regulacion_id):
    """Obtener regulación por ID"""
    return Regulacion.objects.get(id=regulacion_id)


def get_regulacion_by_codigo(codigo):
    """Obtener regulación por código (DIR, DER, IZQ)"""
    return Regulacion.objects.get(codigo=codigo)


def regulacion_create(data):
    """Crear un nuevo tipo de regulación"""
    return Regulacion.objects.create(**data)


def regulacion_update(regulacion_id, data):
    """Actualizar una regulación"""
    regulacion = Regulacion.objects.get(id=regulacion_id)
    for key, value in data.items():
        setattr(regulacion, key, value)
    regulacion.save()
    return regulacion


def regulacion_delete(regulacion_id):
    """Eliminar una regulación"""
    regulacion = Regulacion.objects.get(id=regulacion_id)
    regulacion.delete()


# ========== NODO MOVIMIENTO SERVICES ==========

def get_all_nodos_movimientos():
    """Obtener todas las configuraciones de nodo-movimiento"""
    return NodoMovimiento.objects.all()


def get_nodos_movimientos_by_proyecto(proyecto_id):
    """Obtener configuraciones de un proyecto"""
    return NodoMovimiento.objects.filter(proyecto_id=proyecto_id).select_related(
        'nodo',  'arco_entrada', 'arco_salida', 'regulacion'
    )


def get_nodos_movimientos_by_nodo(nodo_id):
    """Obtener configuraciones de un nodo específico"""
    return NodoMovimiento.objects.filter(nodo_id=nodo_id).select_related(
        'movimiento', 'arco_entrada', 'arco_salida'
    )


def get_nodo_movimiento_by_id(nodo_movimiento_id):
    """Obtener configuración por ID"""
    return NodoMovimiento.objects.select_related(
        'nodo', 'movimiento', 'arco_entrada', 'arco_salida', 'proyecto'
    ).get(id=nodo_movimiento_id)


def nodo_movimiento_create(data):
    """Crear una nueva configuración de nodo-movimiento"""
    return NodoMovimiento.objects.create(**data)


def nodo_movimiento_update(nodo_movimiento_id, data):
    """Actualizar una configuración"""
    nodo_mov = NodoMovimiento.objects.get(id=nodo_movimiento_id)
    for key, value in data.items():
        setattr(nodo_mov, key, value)
    nodo_mov.save()
    return nodo_mov


def nodo_movimiento_delete(nodo_movimiento_id):
    """Eliminar una configuración"""
    nodo_mov = NodoMovimiento.objects.get(id=nodo_movimiento_id)
    nodo_mov.delete()


# ========== COEFICIENTE CRUCE SERVICES ==========

def get_all_coeficientes():
    """Obtener todos los coeficientes de cruce"""
    return Coeficiente_Cruce.objects.all()


def get_coeficiente_by_id(coeficiente_id):
    """Obtener coeficiente por ID"""
    return Coeficiente_Cruce.objects.get(id=coeficiente_id)


def get_coeficiente_by_nomenclatura(nomenclatura):
    """Obtener coeficiente por nomenclatura (VL, TXC, etc.)"""
    return Coeficiente_Cruce.objects.get(nomenclatura=nomenclatura)


def get_coeficientes_standard():
    """Obtener coeficientes estándar"""
    return Coeficiente_Cruce.objects.filter(is_standard=True)


def coeficiente_create(data):
    """Crear un nuevo coeficiente"""
    return Coeficiente_Cruce.objects.create(**data)


def coeficiente_update(coeficiente_id, data):
    """Actualizar un coeficiente"""
    coeficiente = Coeficiente_Cruce.objects.get(id=coeficiente_id)
    for key, value in data.items():
        setattr(coeficiente, key, value)
    coeficiente.save()
    return coeficiente


def coeficiente_delete(coeficiente_id):
    """Eliminar un coeficiente"""
    coeficiente = Coeficiente_Cruce.objects.get(id=coeficiente_id)
    coeficiente.delete()


# ========== IMPORT/EXPORT SERVICES ==========

def import_calles_from_excel(proyecto_id, calles_data):
    """Importar calles desde datos de Excel"""
    calles_creadas = []
    for data in calles_data:
        data['proyecto_id'] = proyecto_id
        calle = Calle.objects.create(**data)
        calles_creadas.append(calle)
    return calles_creadas


def import_nodos_from_excel(proyecto_id, nodos_data, calles_mapping):
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


def import_arcos_from_excel(proyecto_id, arcos_data, nodos_mapping):
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
