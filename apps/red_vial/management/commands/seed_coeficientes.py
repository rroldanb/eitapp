# management/commands/seed_coeficientes.py
# Poblar la librería estándar inicial

from django.core.management.base import BaseCommand
from apps.red_vial.models import CoeficienteCruce

ESTANDARES = [
    ('vl',      'Vehículo liviano',   1.0),
    ('txc',     'Taxi colectivo',     2.0),
    ('txb',     'Taxi básico',        2.0),
    ('c2e',     'Camión 2 ejes',      2.5),
    ('c_mas2e', 'Camión +2 ejes',     3.5),
    ('peat',    'Peatón',             0.2),
    ('cicl',    'Ciclista',           0.5),
    ('moto',    'Motocicleta',        0.75),
]

class Command(BaseCommand):
    help = 'Crea los coeficientes de cruce estándar iniciales'

    def handle(self, *args, **kwargs):
        for nomenclatura, tipo, coef in ESTANDARES:
            obj, created = CoeficienteCruce.objects.get_or_create(
                nomenclatura=nomenclatura,
                proyecto=None,
                defaults={'tipo_transporte': tipo, 'coeficiente': coef, 'is_standard': True}
            )
            status = 'creado' if created else 'ya existe'
            self.stdout.write(f"  {nomenclatura}: {status}")