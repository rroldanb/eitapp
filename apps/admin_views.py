from django.http import HttpResponse
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
from io import BytesIO, StringIO
from datetime import datetime
import os
import tempfile
import zipfile
import re
from .common.utils.excel_utils import generar_plantilla_bytes


def _validate_backup_name(backup_name: str) -> None:
    if not backup_name:
        raise ValueError('Debe indicar un nombre de archivo.')
    if not re.fullmatch(r'[A-Za-z0-9_-]+', backup_name):
        raise ValueError('El nombre del archivo solo puede contener letras, números, guiones y guiones bajos.')


@staff_member_required
def descargar_plantilla(request):
    buf = generar_plantilla_bytes()
    response = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="plantilla_importacion_eitapp.xlsx"'
    return response


@staff_member_required
def backup_database(request):
    default_backup_name = datetime.now().strftime('respaldo_%Y_%m_%d_%H%M%S')
    backup_name = default_backup_name
    error_message = ''

    if request.method == 'POST':
        backup_name = request.POST.get('backup_name', '').strip()

        try:
            _validate_backup_name(backup_name)
            dump_buffer = StringIO()
            call_command('dumpdata', '--natural-primary', '--natural-foreign', '--indent', '2', stdout=dump_buffer)

            bytes_buffer = BytesIO()
            with zipfile.ZipFile(bytes_buffer, 'w', compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr('dumpdata.json', dump_buffer.getvalue().encode('utf-8'))

            bytes_buffer.seek(0)
            response = HttpResponse(bytes_buffer.read(), content_type='application/zip')
            response['Content-Disposition'] = f'attachment; filename="{backup_name}.zip"'
            return response
        except Exception as error:
            error_message = str(error)

    return render(request, 'admin/backup_database.html', {
        'backup_name': backup_name,
        'error_message': error_message,
    })


@staff_member_required
def restore_database(request):
    error_message = ''
    success_message = ''
    database_choices = list(settings.DATABASES.keys())
    target_database = database_choices[0] if database_choices else 'default'
    preserve_requested = False

    if request.method == 'POST':
        backup_file = request.FILES.get('backup_file')
        target_database = request.POST.get('target_database', 'default').strip()
        preserve_requested = request.POST.get('preserve_superuser') == 'on'

        # Validate target database
        if target_database not in database_choices:
            target_database = 'default'

        if not backup_file:
            error_message = 'Debes seleccionar un archivo ZIP de respaldo para restaurar.'
        elif not backup_file.name.lower().endswith('.zip'):
            error_message = 'El archivo debe ser un ZIP válido que contenga el respaldo.'
        else:
            preserved_superuser = None
            UserModel = get_user_model()

            # Only preserve superuser if requested AND user is a superuser
            if preserve_requested and request.user.is_authenticated and request.user.is_superuser:
                preserved_superuser = {}
                for field in request.user._meta.concrete_fields:
                    if field.name == 'id':
                        preserved_superuser['pk'] = getattr(request.user, field.attname)
                    else:
                        preserved_superuser[field.name] = getattr(request.user, field.attname)

            try:
                with zipfile.ZipFile(backup_file, 'r') as archive:
                    if 'dumpdata.json' not in archive.namelist():
                        raise ValueError('El ZIP no contiene el respaldo esperado (dumpdata.json).')
                    dump_bytes = archive.read('dumpdata.json')

                with tempfile.NamedTemporaryFile(mode='wb', suffix='.json', delete=False) as tmp_file:
                    tmp_file.write(dump_bytes)
                    tmp_path = tmp_file.name

                try:
                    call_command('flush', database=target_database, interactive=False, verbosity=0)
                    call_command('migrate', database=target_database, no_input=True, run_syncdb=True)
                    call_command('loaddata', tmp_path, database=target_database)

                    if preserved_superuser:
                        username_field = UserModel.USERNAME_FIELD
                        lookup = {username_field: preserved_superuser[username_field]}
                        defaults = {
                            key: value
                            for key, value in preserved_superuser.items()
                            if key != username_field
                        }
                        UserModel.objects.using(target_database).update_or_create(defaults=defaults, **lookup)
                finally:
                    try:
                        os.unlink(tmp_path)
                    except OSError:
                        pass

                success_message = (
                    f'Restauración completada en la base de datos "{target_database}". '
                    f'Se eliminó toda la data ingresada después del respaldo seleccionado.'
                )
                if preserved_superuser:
                    success_message += ' El usuario superadmin que ejecutó la restauración se conservó en la base de datos.'
            except Exception as error:
                error_message = str(error)

    return render(request, 'admin/restore_database.html', {
        'error_message': error_message,
        'success_message': success_message,
        'database_choices': database_choices,
        'target_database': target_database,
        'preserve_requested': preserve_requested,
    })
