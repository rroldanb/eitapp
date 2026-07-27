from rest_framework import serializers

from apps.red_vial.models import (
    Arco,
    Calle,
    CoeficienteCruce,
    ConfiguracionTransyt,
    FaseSemaforica,
    Nodo,
    ParametroArco,
    Periodizacion,
    Periodo,
    PuntoControl,
    Regulacion,
    ResumenFlujo,
)


class CalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Calle
        fields = ("id", "nombre", "numero", "proyecto")
        read_only_fields = ("id", "created_at", "updated_at")


class NodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nodo
        fields = (
            "id",
            "numero",
            "interseccion",
            "plano",
            "imagen",
            "calle_1",
            "calle_2",
            "proyecto",
            "numero_pc",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ArcoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Arco
        fields = ("id", "nodo_origen", "nodo_destino", "longitud", "proyecto")
        read_only_fields = ("id", "created_at", "updated_at")


class RegulacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Regulacion
        fields = ("id", "codigo", "descripcion")
        read_only_fields = ("id", "created_at", "updated_at")


class CoeficienteCruceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoeficienteCruce
        fields = ("id", "nomenclatura", "tipo_transporte", "coeficiente", "is_standard", "proyecto")
        read_only_fields = ("id", "created_at", "updated_at")


class PuntoControlSerializer(serializers.ModelSerializer):
    class Meta:
        model = PuntoControl
        fields = (
            "id",
            "proyecto",
            "nodo",
            "movimiento",
            "viraje",
            "is_prioritario",
            "arco_entrada",
            "arco_salida",
            "regulacion",
            "numero_pistas",
            "interseccion",
            "vel_ini",
            "vel_mod",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class PeriodoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodo
        fields = ("id", "proyecto", "codigo", "hora_inicio", "hora_fin", "es_laboral")
        read_only_fields = ("id", "created_at", "updated_at")


class PeriodizacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Periodizacion
        fields = (
            "id",
            "fecha",
            "pc",
            "pc_mov",
            "periodo",
            "hora",
            "vl",
            "txc",
            "txb",
            "c2e",
            "c_mas2e",
            "peat",
            "cicl",
            "moto",
            "ftot",
        )
        read_only_fields = ("id", "created_at", "updated_at", "ftot")


class ResumenFlujoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumenFlujo
        fields = (
            "id",
            "pc",
            "periodo",
            "flujo",
            "flujo_total",
            "promedio",
            "num_registros",
            "interseccion_valor",
            "velocidad_inicial",
            "velocidad_modelo",
        )
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "flujo",
            "flujo_total",
            "promedio",
            "num_registros",
        )


class ConfiguracionTransytSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConfiguracionTransyt
        fields = (
            "id",
            "proyecto",
            "ciclo",
            "W",
            "K",
            "perdida_inicial",
            "ganancia_final",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ParametroArcoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ParametroArco
        fields = (
            "id",
            "proyecto",
            "punto_control",
            "flujo_saturacion",
            "ponderador_demora",
            "ponderador_detencion",
            "capacidad_cola",
            "tiene_tarjeta_38",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class FaseSemaforicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = FaseSemaforica
        fields = (
            "id",
            "proyecto",
            "punto_control",
            "fase_numero",
            "verde_inicio",
            "verde_fin",
        )
        read_only_fields = ("id", "created_at", "updated_at")
