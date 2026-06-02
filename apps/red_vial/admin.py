from django.contrib import admin
from .models import *
from .models.trafico import *


class CalleAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'numero', 'proyecto')
    list_filter = ('proyecto',)
    search_fields = ('nombre', 'numero')


class NodoAdmin(admin.ModelAdmin):
    list_display = ('numero', 'interseccion', 'proyecto', 'calle_1', 'calle_2')
    list_filter = ('proyecto',)
    search_fields = ('numero', 'interseccion', 'calle_1__nombre', 'calle_2__nombre')


class ArcoAdmin(admin.ModelAdmin):
    list_display = ('nodo_origen', 'nodo_destino', 'longitud', 'proyecto')
    list_filter = ('proyecto',)
    search_fields = ('nodo_origen__numero', 'nodo_destino__numero')


class RegulacionAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'descripcion')
    search_fields = ('codigo', 'descripcion')


class NodoMovimientoAdmin(admin.ModelAdmin):
    list_display = ('nodo', 'movimiento', 'tipo_prioridad', 'regulacion', 'proyecto')
    list_filter = ('tipo_prioridad', 'regulacion', 'proyecto')
    search_fields = ('nodo__numero', 'movimiento__codigo')


class CoeficienteCruceAdmin(admin.ModelAdmin):
    list_display = ('nomenclatura', 'tipo_transporte', 'coeficiente', 'is_standard')
    list_filter = ('is_standard',)
    search_fields = ('nomenclatura', 'tipo_transporte')


class PeriodoAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'proyecto', 'hora_inicio', 'hora_fin', 'es_laboral')
    list_filter = ('proyecto', 'es_laboral')
    search_fields = ('codigo',)


class ConteoVehicularAdmin(admin.ModelAdmin):
    list_display = ('nodo', 'hora', 'periodo', 'vehiculos_equivalentes')
    list_filter = ('periodo', 'proyecto')
    search_fields = ('nodo__numero',)


class FlujoMovimientoAdmin(admin.ModelAdmin):
    list_display = ('nodo_movimiento', 'hora', 'periodo', 'flujo_veq_hora')
    list_filter = ('periodo', 'proyecto')
    search_fields = ('nodo_movimiento__nodo__numero',)


class PuntoControlAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'nodo', 'movimiento', 'viraje', 'is_prioritario', 'proyecto')
    list_filter = ('is_prioritario', 'viraje', 'proyecto')
    search_fields = ('nombre', 'nodo__numero')


class PeriodizacionAdmin(admin.ModelAdmin):
    list_display = ('pc', 'periodo', 'hora', 'ftot')
    list_filter = ('periodo',)
    search_fields = ('pc__nombre',)


class ResumenFlujoAdmin(admin.ModelAdmin):
    list_display = ('pc', 'periodo', 'flujo', 'flujo_total', 'interseccion_valor')
    list_filter = ('periodo',)
    search_fields = ('pc__nombre',)


class CoeficienteCruceProyectoAdmin(admin.ModelAdmin):
    list_display = ('nomenclatura', 'tipo_transporte', 'coeficiente', 'is_standard', 'proyecto')
    list_filter = ('is_standard',)
    search_fields = ('nomenclatura', 'tipo_transporte')


admin.site.register(Calle, CalleAdmin)
admin.site.register(Nodo, NodoAdmin)
admin.site.register(Arco, ArcoAdmin)
admin.site.register(Regulacion, RegulacionAdmin)
admin.site.register(NodoMovimiento, NodoMovimientoAdmin)
admin.site.register(Coeficiente_Cruce, CoeficienteCruceAdmin)
admin.site.register(Periodo, PeriodoAdmin)
admin.site.register(ConteoVehicular, ConteoVehicularAdmin)
admin.site.register(FlujoMovimiento, FlujoMovimientoAdmin)
admin.site.register(PuntoControl, PuntoControlAdmin)
admin.site.register(Periodizacion, PeriodizacionAdmin)
admin.site.register(ResumenFlujo, ResumenFlujoAdmin)
admin.site.register(CoeficienteCruce, CoeficienteCruceProyectoAdmin)
