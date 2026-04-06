from django.contrib import admin
from .models.proyecto import Proyecto, Imagenes_proyecto


class ImagenesProyectoInline(admin.TabularInline):
    model = Imagenes_proyecto


class ProyectoAdmin(admin.ModelAdmin):
    list_display = ('title', 'mandante', 'date_completed')
    search_fields = ('title', 'mandante__name')
    list_filter = ('date_completed',)
    inlines = [ImagenesProyectoInline]

admin.site.register(Proyecto, ProyectoAdmin)


admin.site.register(Imagenes_proyecto)