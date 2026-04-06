from django.contrib import admin
from .models.mandante import Mandante, Contacto

class MandanteAdmin(admin.ModelAdmin):
    list_display = ('name', 'location')
    search_fields = ('name', 'location')

class ContactoAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'cargo')
    search_fields = ('name', 'email')

admin.site.register(Mandante, MandanteAdmin)
admin.site.register(Contacto, ContactoAdmin)

# Register your models here.
