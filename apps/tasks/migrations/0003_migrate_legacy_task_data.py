from django.db import migrations


def migrate_legacy_data(apps, schema_editor):
    Task = apps.get_model("tasks", "Task")
    for task in Task.objects.all():
        task.created_by = task.user
        task.assignee = task.user
        if task.is_completed:
            task.status = "completada"
            task.date_completed = task.date_completed
        else:
            task.status = "pendiente"
        task.save()


class Migration(migrations.Migration):
    dependencies = [
        ("tasks", "0002_add_new_task_fields"),
    ]

    operations = [
        # migrations.RunPython(migrate_legacy_data),
    ]
