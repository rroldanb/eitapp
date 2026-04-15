from django.contrib import admin
from .models.red_vial import *
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
    list_display = ('codigo', 'nombre', 'tipo_dia')
    list_filter = ('tipo_dia',)
    search_fields = ('codigo', 'nombre')


class ConteoVehicularAdmin(admin.ModelAdmin):
    list_display = ('nodo', 'hora', 'periodo', 'vehiculos_equivalentes')
    list_filter = ('periodo', 'proyecto')
    search_fields = ('nodo__numero',)


class FlujoMovimientoAdmin(admin.ModelAdmin):
    list_display = ('nodo_movimiento', 'hora', 'periodo', 'flujo_veq_hora')
    list_filter = ('periodo', 'proyecto')
    search_fields = ('nodo_movimiento__nodo__numero',)


admin.site.register(Calle, CalleAdmin)
admin.site.register(Nodo, NodoAdmin)
admin.site.register(Arco, ArcoAdmin)
admin.site.register(Regulacion, RegulacionAdmin)
admin.site.register(NodoMovimiento, NodoMovimientoAdmin)
admin.site.register(Coeficiente_Cruce, CoeficienteCruceAdmin)
admin.site.register(Periodo, PeriodoAdmin)
admin.site.register(ConteoVehicular, ConteoVehicularAdmin)
admin.site.register(FlujoMovimiento, FlujoMovimientoAdmin)
