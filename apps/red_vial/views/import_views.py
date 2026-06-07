import json
import copy

from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from django.template.loader import render_to_string

from apps.proyectos.models import Proyecto
from apps.red_vial.services.import_service import parse_excel, validate_selection, execute_import

SESSION_PREFIX = 'import_'


def _clear_import_session(request):
    keys = [k for k in request.session.keys() if k.startswith(SESSION_PREFIX)]
    for k in keys:
        del request.session[k]


def _step_data(request):
    return {
        'parsed': request.session.get(f'{SESSION_PREFIX}parsed'),
        'filename': request.session.get(f'{SESSION_PREFIX}filename'),
        'selected': request.session.get(f'{SESSION_PREFIX}selected'),
        'validation': request.session.get(f'{SESSION_PREFIX}validation'),
        'report': request.session.get(f'{SESSION_PREFIX}report'),
    }


STEPS_DATA = [
    (1, 'Subir Excel'),
    (2, 'Seleccionar'),
    (3, 'Validar'),
    (5, 'Reporte'),
]


def _build_response(request, proyecto, step, content_template, extra=None):
    data = _step_data(request)
    ctx = {
        'proyecto': proyecto,
        'current_step': step,
        'steps_data': STEPS_DATA,
        'parsed': data['parsed'],
        'filename': data['filename'],
        'selected': data['selected'],
        'validation': data['validation'],
        'report': data['report'],
        'report_totals': request.session.get(f'{SESSION_PREFIX}report_totals'),
        'report_json': json.dumps(data['report'] or {}),
        'report_totals_json': json.dumps(request.session.get(f'{SESSION_PREFIX}report_totals') or {}),
    }
    if extra:
        ctx.update(extra)

    content_html = render_to_string(content_template, ctx)
    stepper_html = render_to_string('partials/Import/stepper.html', ctx)

    response = HttpResponse(
        content_html +
        '<div id="import-stepper-bar" hx-swap-oob="true">' +
        stepper_html +
        '</div>'
    )
    return response


@login_required
def import_start(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    _clear_import_session(request)
    from_sidebar = request.GET.get('from_sidebar')
    if from_sidebar:
        request.session[f'{SESSION_PREFIX}from_sidebar'] = True
    return render(request, 'red_vial/importar.html', {
        'proyecto': proyecto,
        'current_step': 1,
        'steps_data': STEPS_DATA,
    })


@login_required
@require_POST
def import_upload(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    _clear_import_session(request)

    excel_file = request.FILES.get('file')
    if not excel_file:
        return _build_response(request, proyecto, 1, 'partials/Import/paso1_upload.html',
                               {'error': 'Debes seleccionar un archivo Excel'})

    if not excel_file.name.endswith(('.xlsx', '.xls')):
        return _build_response(request, proyecto, 1, 'partials/Import/paso1_upload.html',
                               {'error': 'Solo se aceptan archivos .xlsx o .xls'})

    try:
        parsed = parse_excel(excel_file)
    except Exception as e:
        return _build_response(request, proyecto, 1, 'partials/Import/paso1_upload.html',
                               {'error': f'Error al leer el archivo: {e}'})

    if not parsed:
        return _build_response(request, proyecto, 1, 'partials/Import/paso1_upload.html',
                               {'error': 'El archivo no contiene datos válidos en ninguna hoja'})

    request.session[f'{SESSION_PREFIX}parsed'] = parsed
    request.session[f'{SESSION_PREFIX}filename'] = excel_file.name

    # build preview (first 5 rows per sheet)
    preview = {}
    for sheet_name, rows in parsed.items():
        preview[sheet_name] = rows[:5]

    return _build_response(request, proyecto, 1, 'partials/Import/paso1_upload.html',
                           {'preview': preview, 'uploaded': True})


@login_required
@require_POST
def import_back_step1(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    keys = [k for k in request.session.keys() if k.startswith(f'{SESSION_PREFIX}parsed') or k.startswith(f'{SESSION_PREFIX}filename') or k.startswith(f'{SESSION_PREFIX}selected') or k.startswith(f'{SESSION_PREFIX}validation') or k.startswith(f'{SESSION_PREFIX}report') or k.startswith(f'{SESSION_PREFIX}report_totals')]
    for k in keys:
        del request.session[k]
    return _build_response(request, proyecto, 1, 'partials/Import/paso1_upload.html',
                           {'message': 'Selecciona un archivo Excel para importar.'})


@login_required
@require_POST
def import_goto_selection(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    data = _step_data(request)
    if not data['parsed']:
        return _build_response(request, proyecto, 1, 'partials/Import/paso1_upload.html',
                               {'error': 'Sesión expirada. Vuelve a subir el archivo.'})
    return _build_response(request, proyecto, 2, 'partials/Import/paso2_seleccion.html',
                           {'from_sidebar': request.session.get(f'{SESSION_PREFIX}from_sidebar')})


@login_required
@require_POST
def import_validate(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    data = _step_data(request)
    parsed = data['parsed']
    if not parsed:
        return _build_response(request, proyecto, 1, 'partials/Import/paso1_upload.html',
                               {'error': 'Sesión expirada. Vuelve a subir el archivo.'})

    selected = request.POST.getlist('sheets')
    if not selected:
        return _build_response(request, proyecto, 2, 'partials/Import/paso2_seleccion.html',
                               {'error': 'Debes seleccionar al menos una hoja',
                                'from_sidebar': request.session.get(f'{SESSION_PREFIX}from_sidebar')})

    request.session[f'{SESSION_PREFIX}selected'] = selected
    validation = validate_selection(parsed, selected, proyecto)
    request.session[f'{SESSION_PREFIX}validation'] = validation

    return _build_response(request, proyecto, 3, 'partials/Import/paso3_validacion.html')


@login_required
@require_POST
def import_execute(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    data = _step_data(request)
    validation = data['validation']
    if not validation:
        return _build_response(request, proyecto, 1, 'partials/Import/paso1_upload.html',
                               {'error': 'Sesión expirada. Vuelve a empezar.'})

    # read duplicate handling choices
    update_duplicates = {}
    for key in request.POST:
        if key.startswith('dup_'):
            sheet = key[4:]
            update_duplicates[sheet] = request.POST[key] == 'update'

    try:
        report = execute_import(copy.deepcopy(validation), proyecto, request.user, update_duplicates)
        # compute totals
        total_inserted = sum(sr.get('inserted', 0) for sr in report.values())
        total_updated = sum(sr.get('updated', 0) for sr in report.values())
        total_skipped = sum(sr.get('skipped_duplicates', 0) for sr in report.values())
        total_rejected = sum(len(sr.get('rejected', [])) for sr in report.values())
        request.session[f'{SESSION_PREFIX}report'] = report
        request.session[f'{SESSION_PREFIX}report_totals'] = {
            'inserted': total_inserted,
            'updated': total_updated,
            'skipped': total_skipped,
            'rejected': total_rejected,
        }
    except Exception as e:
        return _build_response(request, proyecto, 3, 'partials/Import/paso3_validacion.html',
                               {'error': f'Error durante la importación: {e}'})

    return _build_response(request, proyecto, 5, 'partials/Import/paso5_reporte.html')


@login_required
@require_POST
def import_cancel(request, proyecto_id):
    proyecto = get_object_or_404(Proyecto, id=proyecto_id)
    _clear_import_session(request)
    return _build_response(request, proyecto, 1, 'partials/Import/paso1_upload.html',
                           {'message': 'Importación cancelada.'})


@login_required
def import_project_select(request):
    proyectos = Proyecto.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'red_vial/import_project_select.html', {
        'proyectos': proyectos,
    })
