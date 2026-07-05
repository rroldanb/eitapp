from django.db.models import Count
from django.shortcuts import get_object_or_404

from apps.mandantes.models import Contacto, Mandante


def get_all_mandantes():
    return Mandante.objects.annotate(contactos_count=Count("contactos"))


def get_mandante_by_id(mandante_id):
    return get_object_or_404(Mandante.objects.prefetch_related("contactos"), id=mandante_id)


def mandante_create(data):
    return Mandante.objects.create(**data)


def mandante_delete(mandante_id):
    mandante = get_object_or_404(Mandante, id=mandante_id)
    mandante.delete()


def get_contacto_by_id(contacto_id):
    return get_object_or_404(Contacto, id=contacto_id)


def contacto_create(data):
    return Contacto.objects.create(**data)


def contacto_delete(contacto_id):
    contacto = get_object_or_404(Contacto, id=contacto_id)
    contacto.delete()


def get_contactos_by_mandante(mandante_id):
    return Contacto.objects.filter(mandante_id=mandante_id)
