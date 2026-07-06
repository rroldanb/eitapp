from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0003_migrate_legacy_task_data"),
    ]

    operations = [
        # migrations.RemoveField(
        #     model_name='task',
        #     name='is_completed',
        # ),
        # migrations.RemoveField(
        #     model_name='task',
        #     name='user',
        # ),
        # migrations.AlterField(
        #     model_name='task',
        #     name='created_by',
        #     field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_tasks', to='auth.user'),
        # ),
    ]
