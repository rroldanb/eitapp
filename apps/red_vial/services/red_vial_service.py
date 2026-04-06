from apps.red_vial.models import (
    Calle,
    Nodo,
    Arco,
    Movimiento,
    NodoMovimiento,
    Coeficiente_Cruce,
)
from apps.proyectos.models import Proyecto


# ========== CALLE SERVICES ==========

def get_all_calles():
    """Obtener todas las calles"""
    return Calle.objects.all()


def get_calles_by_proyecto(proyecto_id):
    """Obtener calles de un proyecto"""
    return Calle.objects.filter(proyecto_id=proyecto_id)


def get_calle_by_id(calle_id):
    """Obtener calle por ID"""
    return Calle.objects.get(id=calle_id)


def calle_create(data):
    """Crear una nueva calle"""
    return Calle.objects.create(**data)


def calle_update(calle_id, data):
    """Actualizar una calle"""
    calle = Calle.objects.get(id=calle_id)
    for key, value in data.items():
        setattr(calle, key, value)
    calle.save()
    return calle


def calle_delete(calle_id):
    """Eliminar una calle"""
    calle = Calle.objects.get(id=calle_id)
    calle.delete()


# ========== NODO SERVICES ==========

def get_all_nodos():
    """Obtener todos los nodos"""
    return Nodo.objects.all()


def get_nodos_by_proyecto(proyecto_id):
    """Obtener nodos de un proyecto con calles relacionadas"""
    return Nodo.objects.filter(proyecto_id=proyecto_id).select_related('calle_1', 'calle_2')


def get_nodo_by_id(nodo_id):
    """Obtener nodo por ID con calles relacionadas"""
    return Nodo.objects.select_related('calle_1', 'calle_2', 'proyecto').get(id=nodo_id)


def nodo_create(data):
    """Crear un nuevo nodo"""
    return Nodo.objects.create(**data)


def nodo_update(nodo_id, data):
    """Actualizar un nodo"""
    nodo = Nodo.objects.get(id=nodo_id)
    for key, value in data.items():
        setattr(nodo, key, value)
    nodo.save()
    return nodo


def nodo_delete(nodo_id):
    """Eliminar un nodo"""
    nodo = Nodo.objects.get(id=nodo_id)
    nodo.delete()


# ========== ARCO SERVICES ==========

def get_all_arcos():
    """Obtener todos los arcos"""
    return Arco.objects.all()


def get_arcos_by_proyecto(proyecto_id):
    """Obtener arcos de un proyecto con nodos relacionados"""
    return Arco.objects.filter(proyecto_id=proyecto_id).select_related('nodo_origen', 'nodo_destino')


def get_arco_by_id(arco_id):
    """Obtener arco por ID con nodos relacionados"""
    return Arco.objects.select_related('nodo_origen', 'nodo_destino', 'proyecto').get(id=arco_id)


def arco_create(data):
    """Crear un nuevo arco"""
    return Arco.objects.create(**data)


def arco_update(arco_id, data):
    """Actualizar un arco"""
    arco = Arco.objects.get(id=arco_id)
    for key, value in data.items():
        setattr(arco, key, value)
    arco.save()
    return arco


def arco_delete(arco_id):
    """Eliminar un arco"""
    arco = Arco.objects.get(id=arco_id)
    arco.delete()


def get_arcos_by_nodo(nodo_id):
    """Obtener arcos conectados a un nodo (origen o destino)"""
    from django.db.models import Q
    return Arco.objects.filter(
        Q(nodo_origen_id=nodo_id) | Q(nodo_destino_id=nodo_id)
    ).select_related('nodo_origen', 'nodo_destino')


# ========== MOVIMIENTO SERVICES ==========

def get_all_movimientos():
    """Obtener todos los tipos de movimiento"""
    return Movimiento.objects.all()


def get_movimiento_by_id(movimiento_id):
    """Obtener movimiento por ID"""
    return Movimiento.objects.get(id=movimiento_id)


def get_movimiento_by_codigo(codigo):
    """Obtener movimiento por código (DIR, DER, IZQ)"""
    return Movimiento.objects.get(codigo=codigo)


def movimiento_create(data):
    """Crear un nuevo tipo de movimiento"""
    return Movimiento.objects.create(**data)


def movimiento_update(movimiento_id, data):
    """Actualizar un movimiento"""
    movimiento = Movimiento.objects.get(id=movimiento_id)
    for key, value in data.items():
        setattr(movimiento, key, value)
    movimiento.save()
    return movimiento


def movimiento_delete(movimiento_id):
    """Eliminar un movimiento"""
    movimiento = Movimiento.objects.get(id=movimiento_id)
    movimiento.delete()


# ========== NODO MOVIMIENTO SERVICES ==========

def get_all_nodos_movimientos():
    """Obtener todas las configuraciones de nodo-movimiento"""
    return NodoMovimiento.objects.all()


def get_nodos_movimientos_by_proyecto(proyecto_id):
    """Obtener configuraciones de un proyecto"""
    return NodoMovimiento.objects.filter(proyecto_id=proyecto_id).select_related(
        'nodo', 'movimiento', 'arco_entrada', 'arco_salida'
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
