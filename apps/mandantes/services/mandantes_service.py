from apps.mandantes.models import Mandante, Contacto


def get_all_mandantes():
    return Mandante.objects.all()


def get_mandante_by_id(mandante_id):
    return Mandante.objects.prefetch_related("contactos").get(id=mandante_id)


def mandante_create(data):
    return Mandante.objects.create(**data)

def mandante_delete(mandante_id):
    mandante = Mandante.objects.get(id=mandante_id)
    mandante.delete()


def get_contacto_by_id(contacto_id):
    return Contacto.objects.get(id=contacto_id)


def contacto_create(data):
    return Contacto.objects.create(**data)

def contacto_delete(contacto_id):
    contacto = Contacto.objects.get(id=contacto_id)
    contacto.delete()

def get_contactos_by_mandante(mandante_id):
    return Contacto.objects.filter(mandante_id=mandante_id)




