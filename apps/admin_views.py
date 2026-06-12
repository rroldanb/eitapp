from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, get_object_or_404
from django.core.management import call_command
from django.contrib.auth import get_user_model
from django.db import transaction
from django.conf import settings
from django.urls import reverse
from io import BytesIO, StringIO
from datetime import datetime
import os
import tempfile
import zipfile
import re
import uuid
import pandas as pd
from .common.utils.excel_utils import generar_plantilla_bytes
from .common.utils.migra_cli import run_from_bytes
from apps.mandantes.models import Mandante
from apps.proyectos.models import Proyecto

_migration_cache = {}


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


# ── Migración TRANSYT ────────────────────────────────────────────────────────


@staff_member_required
def migracion_gui(request):
    proyectos = Proyecto.objects.filter(is_completed=False)
    mandantes = Mandante.objects.all()

    if request.method == 'POST':
        archivo = request.FILES.get('archivo_origen')
        if not archivo or not archivo.name.lower().endswith('.xlsx'):
            return render(request, 'admin/migracion_gui.html', {
                'error_message': 'Debes seleccionar un archivo .xlsx de origen.',
                'proyectos': proyectos, 'mandantes': mandantes,
            })

        fecha = request.POST.get('fecha', '').strip() or '01/01/2024'
        destino_tipo = request.POST.get('destino_tipo', 'nuevo')
        proyecto_data = {}

        if destino_tipo == 'existente':
            proyecto_id = request.POST.get('proyecto_id')
            if not proyecto_id:
                return render(request, 'admin/migracion_gui.html', {
                    'error_message': 'Debes seleccionar un proyecto existente.',
                    'proyectos': proyectos, 'mandantes': mandantes,
                })
            p = get_object_or_404(Proyecto, id=proyecto_id)
            proyecto_data = {
                'proyecto_title': p.title,
                'proyecto_description': p.description or '',
                'proyecto_date_started': p.date_started.strftime('%d/%m/%Y') if p.date_started else '',
                'mandante_name': p.mandante.name,
                'mandante_location': p.mandante.location or '',
                'mandante_details': p.mandante.details or '',
                'contacto_name': '', 'contacto_email': '', 'contacto_phone': '',
                'contacto_cargo': '', 'contacto_position': '',
            }
        else:
            proyecto_title = request.POST.get('proyecto_title', '').strip()
            if not proyecto_title:
                return render(request, 'admin/migracion_gui.html', {
                    'error_message': 'Debes ingresar un nombre para el nuevo proyecto.',
                    'proyectos': proyectos, 'mandantes': mandantes,
                })
            if Proyecto.objects.filter(title__iexact=proyecto_title).exists():
                return render(request, 'admin/migracion_gui.html', {
                    'error_message': f'Ya existe un proyecto con el nombre "{proyecto_title}".',
                    'proyectos': proyectos, 'mandantes': mandantes,
                })

            proyecto_description = request.POST.get('proyecto_description', '').strip()
            proyecto_date_started = request.POST.get('proyecto_date_started', '').strip()

            if request.POST.get('mandante_tipo') == 'existente':
                mandante_id = request.POST.get('mandante_id')
                if not mandante_id:
                    return render(request, 'admin/migracion_gui.html', {
                        'error_message': 'Debes seleccionar un mandante existente.',
                        'proyectos': proyectos, 'mandantes': mandantes,
                    })
                m = get_object_or_404(Mandante, id=mandante_id)
                mandante_name = m.name
                mandante_location = m.location or ''
                mandante_details = m.details or ''
            else:
                mandante_name = request.POST.get('mandante_name_new', '').strip()
                mandante_location = request.POST.get('mandante_location_new', '').strip()
                mandante_details = request.POST.get('mandante_details_new', '').strip()
                if not mandante_name:
                    return render(request, 'admin/migracion_gui.html', {
                        'error_message': 'Debes ingresar el nombre del nuevo mandante.',
                        'proyectos': proyectos, 'mandantes': mandantes,
                    })

            proyecto_data = {
                'proyecto_title': proyecto_title,
                'proyecto_description': proyecto_description,
                'proyecto_date_started': proyecto_date_started,
                'mandante_name': mandante_name,
                'mandante_location': mandante_location,
                'mandante_details': mandante_details,
                'contacto_name': '', 'contacto_email': '', 'contacto_phone': '',
                'contacto_cargo': '', 'contacto_position': '',
            }

        destino_bio = generar_plantilla_bytes()

        try:
            out_bio, stats = run_from_bytes(
                origen_bio=archivo, destino_bio=destino_bio,
                fecha=fecha, proyecto_data=proyecto_data,
            )
        except Exception as e:
            return render(request, 'admin/migracion_gui.html', {
                'error_message': f'Error durante la migración: {str(e)}',
                'proyectos': proyectos, 'mandantes': mandantes,
            })

        tmp = tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx')
        tmp.write(out_bio.read())
        tmp_path = tmp.name
        tmp.close()

        token = str(uuid.uuid4())
        _migration_cache[token] = {
            'path': tmp_path,
            'stats': stats,
            'proyecto_data': proyecto_data,
        }

        return HttpResponseRedirect(reverse('migracion_reporte', args=[token]))

    return render(request, 'admin/migracion_gui.html', {
        'proyectos': proyectos, 'mandantes': mandantes,
    })


@staff_member_required
def migracion_reporte(request, token):
    info = _migration_cache.get(token)
    if not info:
        return render(request, 'admin/migracion_gui.html', {
            'error_message': 'El reporte ha expirado o no es válido.',
        })
    return render(request, 'admin/migracion_gui.html', {
        'report': True,
        'token': token,
        'stats': info['stats'],
        'proyecto_data': info['proyecto_data'],
        'sheet_names': ["Calle", "Nodo", "Arco", "PuntoControl", "ParametroArco", "Periodo", "Periodizacion"],
    })


@staff_member_required
def migracion_descarga_xlsx(request, token):
    info = _migration_cache.get(token)
    if not info:
        return HttpResponse('Reporte expirado o inválido.', status=404)
    with open(info['path'], 'rb') as f:
        response = HttpResponse(f.read(), content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
        title = info['proyecto_data'].get('proyecto_title', 'migracion')
        response['Content-Disposition'] = f'attachment; filename="{title}.xlsx"'
        return response


@staff_member_required
def migracion_descarga_csv(request, token, sheet):
    info = _migration_cache.get(token)
    if not info:
        return HttpResponse('Reporte expirado o inválido.', status=404)
    df = pd.read_excel(info['path'], sheet_name=sheet, header=None, skiprows=2)
    df = df.dropna(how='all').reset_index(drop=True)
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{sheet}.csv"'
    df.to_csv(response, index=False, header=False, encoding='utf-8-sig')
    return response
