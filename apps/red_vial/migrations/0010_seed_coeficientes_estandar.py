from django.db import migrations


COEFICIENTES = [
    {"nomenclatura": "VL", "tipo_transporte": "Vehículo ligero", "coeficiente": 1.00},
    {"nomenclatura": "TXC", "tipo_transporte": "Taxi colectivo", "coeficiente": 1.35},
    {"nomenclatura": "TXB", "tipo_transporte": "Bus", "coeficiente": 1.65},
    {"nomenclatura": "C2E", "tipo_transporte": "Camión 2 ejes", "coeficiente": 2.00},
    {"nomenclatura": "C_MAS2E", "tipo_transporte": "Camión más de 2 ejes", "coeficiente": 2.50},
    {"nomenclatura": "PEAT", "tipo_transporte": "Peatón", "coeficiente": 0.00},
    {"nomenclatura": "CICL", "tipo_transporte": "Ciclista", "coeficiente": 0.00},
    {"nomenclatura": "MOTO", "tipo_transporte": "Moto", "coeficiente": 0.60},
]


def seed_coeficientes(apps, schema_editor):
    CoeficienteCruce = apps.get_model("red_vial", "CoeficienteCruce")
    for data in COEFICIENTES:
        CoeficienteCruce.objects.update_or_create(
            nomenclatura=data["nomenclatura"],
            proyecto=None,
            defaults={
                **data,
                "is_standard": True,
            },
        )


def reverse_seed(apps, schema_editor):
    CoeficienteCruce = apps.get_model("red_vial", "CoeficienteCruce")
    CoeficienteCruce.objects.filter(
        nomenclatura__in=[c["nomenclatura"] for c in COEFICIENTES],
        proyecto__isnull=True,
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("red_vial", "0009_alter_periodizacion_unique_together_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_coeficientes, reverse_seed),
    ]
