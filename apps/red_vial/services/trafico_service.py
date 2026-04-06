from apps.red_vial.models import (
    Periodo,
    ConteoVehicular,
    FlujoMovimiento,
    NodoMovimiento,
)


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


# ========== CONTEO VEHICULAR SERVICES ==========

def get_all_conteos():
    """Obtener todos los conteos vehiculares"""
    return ConteoVehicular.objects.all()


def get_conteos_by_proyecto(proyecto_id):
    """Obtener conteos de un proyecto"""
    return ConteoVehicular.objects.filter(proyecto_id=proyecto_id).select_related(
        'nodo', 'periodo'
    )


def get_conteos_by_nodo(nodo_id):
    """Obtener conteos de un nodo específico"""
    return ConteoVehicular.objects.filter(nodo_id=nodo_id).select_related('periodo')


def get_conteos_by_periodo(periodo_id):
    """Obtener conteos de un período"""
    return ConteoVehicular.objects.filter(periodo_id=periodo_id).select_related('nodo')


def get_conteo_by_id(conteo_id):
    """Obtener conteo por ID"""
    return ConteoVehicular.objects.select_related('nodo', 'periodo', 'proyecto').get(id=conteo_id)


def conteo_create(data):
    """Crear un nuevo conteo vehicular"""
    return ConteoVehicular.objects.create(**data)


def conteo_update(conteo_id, data):
    """Actualizar un conteo"""
    conteo = ConteoVehicular.objects.get(id=conteo_id)
    for key, value in data.items():
        setattr(conteo, key, value)
    conteo.save()
    return conteo


def conteo_delete(conteo_id):
    """Eliminar un conteo"""
    conteo = ConteoVehicular.objects.get(id=conteo_id)
    conteo.delete()


def calcular_veq_totales(conteo_id):
    """Calcular vehículos equivalentes totales de un conteo"""
    from apps.red_vial.models import Coeficiente_Cruce

    conteo = ConteoVehicular.objects.get(id=conteo_id)

    # Obtener coeficientes
    coeficientes = {
        'vl': Coeficiente_Cruce.objects.get(nomenclatura='VL').coeficiente,
        'txc': Coeficiente_Cruce.objects.get(nomenclatura='TXC').coeficiente,
        'txb': Coeficiente_Cruce.objects.get(nomenclatura='TXB').coeficiente,
        'c_2e': Coeficiente_Cruce.objects.get(nomenclatura='C 2E').coeficiente,
        'c_mas_2e': Coeficiente_Cruce.objects.get(nomenclatura='C+2E').coeficiente,
        'peaton': Coeficiente_Cruce.objects.get(nomenclatura='Peat').coeficiente,
        'ciclista': Coeficiente_Cruce.objects.get(nomenclatura='Cicl').coeficiente,
        'moto': Coeficiente_Cruce.objects.get(nomenclatura='Moto').coeficiente,
    }

    veq_total = (
        (conteo.vl or 0) * coeficientes['vl'] +
        (conteo.txc or 0) * coeficientes['txc'] +
        (conteo.txb or 0) * coeficientes['txb'] +
        (conteo.c_2e or 0) * coeficientes['c_2e'] +
        (conteo.c_mas_2e or 0) * coeficientes['c_mas_2e'] +
        (conteo.peaton or 0) * coeficientes['peaton'] +
        (conteo.ciclista or 0) * coeficientes['ciclista'] +
        (conteo.moto or 0) * coeficientes['moto']
    )

    conteo.vehiculos_equivalentes = veq_total
    conteo.save()
    return veq_total


# ========== FLUJO MOVIMIENTO SERVICES ==========

def get_all_flujos():
    """Obtener todos los flujos de movimiento"""
    return FlujoMovimiento.objects.all()


def get_flujos_by_proyecto(proyecto_id):
    """Obtener flujos de un proyecto"""
    return FlujoMovimiento.objects.filter(proyecto_id=proyecto_id).select_related(
        'nodo_movimiento', 'periodo'
    )


def get_flujos_by_nodo_movimiento(nodo_movimiento_id):
    """Obtener flujos de un nodo-movimiento específico"""
    return FlujoMovimiento.objects.filter(
        nodo_movimiento_id=nodo_movimiento_id
    ).select_related('periodo')


def get_flujos_by_periodo(periodo_id):
    """Obtener flujos de un período"""
    return FlujoMovimiento.objects.filter(periodo_id=periodo_id).select_related(
        'nodo_movimiento'
    )


def get_flujo_by_id(flujo_id):
    """Obtener flujo por ID"""
    return FlujoMovimiento.objects.select_related(
        'nodo_movimiento', 'periodo', 'proyecto'
    ).get(id=flujo_id)


def flujo_create(data):
    """Crear un nuevo flujo de movimiento"""
    return FlujoMovimiento.objects.create(**data)


def flujo_update(flujo_id, data):
    """Actualizar un flujo"""
    flujo = FlujoMovimiento.objects.get(id=flujo_id)
    for key, value in data.items():
        setattr(flujo, key, value)
    flujo.save()
    return flujo


def flujo_delete(flujo_id):
    """Eliminar un flujo"""
    flujo = FlujoMovimiento.objects.get(id=flujo_id)
    flujo.delete()


# ========== IMPORT/EXPORT SERVICES ==========

def import_conteos_from_excel(proyecto_id, conteos_data):
    """Importar conteos vehiculares desde datos de Excel"""
    conteos_creados = []
    for data in conteos_data:
        data['proyecto_id'] = proyecto_id
        conteo = ConteoVehicular.objects.create(**data)
        conteos_creados.append(conteo)
    return conteos_creados


def import_flujos_from_excel(proyecto_id, flujos_data, nodos_movimientos_mapping):
    """Importar flujos desde datos de Excel"""
    flujos_creados = []
    for data in flujos_data:
        data['proyecto_id'] = proyecto_id
        # Mapear nodo_movimiento si es necesario
        if 'nodo_movimiento_key' in data:
            data['nodo_movimiento_id'] = nodos_movimientos_mapping.get(
                data.pop('nodo_movimiento_key')
            )
        flujo = FlujoMovimiento.objects.create(**data)
        flujos_creados.append(flujo)
    return flujos_creados


# ========== ANALYSIS SERVICES ==========

def get_flujo_promedio_por_periodo(proyecto_id, periodo_id):
    """Calcular flujo promedio por período"""
    from django.db.models import Avg

    return FlujoMovimiento.objects.filter(
        proyecto_id=proyecto_id,
        periodo_id=periodo_id
    ).aggregate(
        promedio_veq_hora=Avg('flujo_veq_hora'),
        promedio_veh_hora=Avg('flujo_veh_hora')
    )


def get_conteo_promedio_por_hora(proyecto_id, hora_inicio, hora_fin):
    """Obtener conteo promedio entre un rango de horas"""
    from django.db.models import Avg

    return ConteoVehicular.objects.filter(
        proyecto_id=proyecto_id,
        hora__gte=hora_inicio,
        hora__lte=hora_fin
    ).aggregate(
        promedio_veq=Avg('vehiculos_equivalentes'),
        promedio_vl=Avg('vl'),
        promedio_txb=Avg('txb'),
        promedio_c2e=Avg('c_2e')
    )


def get_nodos_con_mayor_flujo(proyecto_id, limit=10):
    """Obtener los nodos con mayor flujo de tráfico"""
    from django.db.models import Sum

    return NodoMovimiento.objects.filter(
        proyecto_id=proyecto_id
    ).annotate(
        flujo_total=Sum('flujos__flujo_veq_hora')
    ).order_by('-flujo_total')[:limit]
