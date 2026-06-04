from apps.red_vial.models import Periodo


# ========== PERIODO SERVICES ==========

def get_all_periodos():
    """Obtener todos los períodos"""
    return Periodo.objects.all()


def get_periodo_by_id(periodo_id):
    """Obtener período por ID"""
    return Periodo.objects.get(id=periodo_id)


def get_periodo_by_codigo(codigo):
    """Obtener período por código (PM-L, PT-L, etc.)"""
    return Periodo.objects.get(codigo=codigo)


def periodo_create(data):
    """Crear un nuevo período"""
    return Periodo.objects.create(**data)


def periodo_update(periodo_id, data):
    """Actualizar un período"""
    periodo = Periodo.objects.get(id=periodo_id)
    for key, value in data.items():
        setattr(periodo, key, value)
    periodo.save()
    return periodo


def periodo_delete(periodo_id):
    """Eliminar un período"""
    periodo = Periodo.objects.get(id=periodo_id)
    periodo.delete()
