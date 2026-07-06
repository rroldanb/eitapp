from django.db import migrations


def clean_old_vl(apps, schema_editor):
    CoeficienteCruce = apps.get_model("red_vial", "CoeficienteCruce")
    # Delete the old uppercase VL record that doesn't match Periodizacion field name
    CoeficienteCruce.objects.filter(
        nomenclatura="VL",
        proyecto__isnull=True,
    ).delete()


def reverse_clean(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("red_vial", "0010_seed_coeficientes_estandar"),
    ]

    operations = [
        migrations.RunPython(clean_old_vl, reverse_clean),
    ]
