from django.db import migrations
from django.db.models import F, Func


def uppercase_nomenclatura(apps, schema_editor):
    CoeficienteCruce = apps.get_model("red_vial", "CoeficienteCruce")
    CoeficienteCruce.objects.update(nomenclatura=Func(F("nomenclatura"), function="UPPER"))


def reverse_uppercase(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("red_vial", "0011_fix_coeficiente_vl_case"),
    ]

    operations = [
        migrations.RunPython(uppercase_nomenclatura, reverse_uppercase),
    ]
