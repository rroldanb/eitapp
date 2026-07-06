from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("red_vial", "0013_resumenflujo_num_registros_resumenflujo_promedio"),
    ]

    operations = [
        migrations.DeleteModel(
            name="FlujoMovimiento",
        ),
        migrations.DeleteModel(
            name="ConteoVehicular",
        ),
        migrations.DeleteModel(
            name="NodoMovimiento",
        ),
    ]
