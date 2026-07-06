from django.db import migrations


def create_profiles(apps, schema_editor):
    User = apps.get_model("auth", "User")
    UserProfile = apps.get_model("usuarios", "UserProfile")
    for user in User.objects.all():
        UserProfile.objects.get_or_create(user=user)


def set_initial_roles(apps, schema_editor):
    UserProfile = apps.get_model("usuarios", "UserProfile")
    for profile in UserProfile.objects.filter(role=10):
        if profile.user.is_superuser:
            profile.role = 30
        elif profile.user.is_staff:
            profile.role = 20
        profile.save()


class Migration(migrations.Migration):
    dependencies = [
        ("usuarios", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(create_profiles),
        migrations.RunPython(set_initial_roles),
    ]
