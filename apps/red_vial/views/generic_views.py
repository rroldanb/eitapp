"""
Generic views para operaciones CRUD con soporte HTMX y ordenamiento.
Proporciona clases base reutilizables para todas las entidades de red_vial.
"""
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseBadRequest, JsonResponse
from django.views import View
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError
import json
import inspect


# ========== LIST VIEW GENÉRICA ==========

class GenericListView(View):
    """
    Vista genérica para listar items con soporte de ordenamiento y HTMX.
    
    Atributos requeridos:
        - model: Clase del modelo
        - service_get_function: Función del servicio para obtener items
        - sort_fields: Lista de campos permitidos para sort
        - default_sort: Campo por defecto para ordenar
        - partial_template: Template del partial (para HTMX)
        - full_template: Template de página completa
    """
    
    model = None
    service_get_function = None
    sort_fields = ['id']
    default_sort = 'id'
    partial_template = None
    full_template = None
    context_items_key = 'items'  # Nombre de la variable en el contexto
    form_class = None   

    @method_decorator(login_required)
    def get(self, request, proyecto_id=None):
        """GET: Retorna lista de items, partial si HTMX, página completa si no."""
        # Obtener proyecto_id desde resolver_match para evitar valores mal enlazados
        resolver_kwargs = getattr(request, 'resolver_match', None)
        if resolver_kwargs:
            proyecto_id = resolver_kwargs.kwargs.get('proyecto_id', proyecto_id)

        proyecto = get_object_or_404(self.model._meta.get_field('proyecto').related_model, id=proyecto_id)
        
        # Obtener parámetros de sort
        sort_by = request.GET.get('sort_by', self.default_sort)
        sort_order = request.GET.get('sort_order', 'asc')
        
        # Validar sort_by
        if sort_by not in self.sort_fields:
            sort_by = self.default_sort
        if sort_order not in ['asc', 'desc']:
            sort_order = 'asc'
        
        # Obtener items del servicio
        # Inspeccionar firma para detectar parámetros opcionales (sort_by, order, etc.)
        try:
            sig = inspect.signature(self.service_get_function)
            accepted = set(sig.parameters.keys())
        except (ValueError, TypeError):
            accepted = set()

        # Construir kwargs: SIEMPRE pasar proyecto_id + parámetros opcionales detectados
        call_kwargs = {'proyecto_id': proyecto_id}
        
        if 'sort_by' in accepted:
            call_kwargs['sort_by'] = sort_by
        if 'order' in accepted:
            call_kwargs['order'] = sort_order

        # Acceder a la función desde la clase para evitar que sea convertida a método bound
        service_func = self.__class__.service_get_function
        items = service_func(**call_kwargs)
        
        context = {
            'proyecto': proyecto,
            self.context_items_key: items,
            'sort_by': sort_by,
            'sort_order': sort_order,
            'sort_fields': self.sort_fields,
        }
        
        if self.form_class:
            kwargs = {}
            sig = inspect.signature(self.form_class.__init__)
            if 'proyecto' in sig.parameters:
                kwargs['proyecto'] = proyecto
            context['form'] = self.form_class(**kwargs)

        # Retornar partial si HTMX, página completa si no
        if request.headers.get('HX-Request'):
            return render(request, self.partial_template, context)
        return render(request, self.full_template, context)


# ========== CREATE VIEW GENÉRICA ==========

class GenericCreateView(View):
    """
    Vista genérica para crear items.
    
    Atributos requeridos:
        - model: Clase del modelo
        - form_class: Clase del formulario
        - service_create_function: Función del servicio para crear
        - row_template: Template de la fila (para insertar)
        - form_template: Template del formulario (para errores)
    """
    
    model = None
    form_class = None
    service_create_function = None
    row_template = None
    form_template = None
    
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['POST']))
    def post(self, request, proyecto_id):
        """POST: Crea un item y retorna su fila HTML."""
        from apps.proyectos.models import Proyecto
        
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        
        form_kwargs = {'data': request.POST}
        sig = inspect.signature(self.form_class.__init__)
        if 'proyecto' in sig.parameters:
            form_kwargs['proyecto'] = proyecto
        form = self.form_class(**form_kwargs)
        
        if form.is_valid():
            try:
                service_func = self.__class__.service_create_function
                item = service_func(proyecto, form.cleaned_data)
                # Añadir tanto 'item' genérico como la clave singular del modelo
                # para compatibilidad con templates que esperan el nombre del modelo (ej. 'calle')
                singular = self.model._meta.model_name if self.model is not None else 'item'
                context = {'item': item, 'proyecto': proyecto, singular: item}
                print(f"Context for create response 1 : {context}")  # Debug log

                if self.form_class:
                    kwargs = {}
                    sig = inspect.signature(self.form_class.__init__)
                    if 'proyecto' in sig.parameters:
                        kwargs['proyecto'] = proyecto
                    context['form'] = self.form_class(**kwargs)
                    print(f"Context for create response: {context}")  # Debug log
                return render(request, self.row_template, context)
            except ValidationError as e:
                for err in e.messages:
                    form.add_error(None, str(err))
                return render(request, self.form_template, {
                    'proyecto': proyecto,
                    'form': form,
                }, status=400)
            except IntegrityError as e:
                msg = 'Ya existe un item con la misma clave primaria, revisa los datos ingresados.'
                form.add_error(None, msg)
                response = render(request, self.form_template, {
                    'proyecto': proyecto,
                    'form': form,
                }, status=400)
                response['X-Form-Error'] = msg
                return response
            # except IntegrityError:
            #     form.add_error(None, 'Ya existe un registro con esos valores.')
            #     return render(request, self.form_template, {
            #         'proyecto': proyecto,
            #         'form': form,
            #     }, status=400)
                # return HttpResponseBadRequest(
                #     json.dumps({'error': str(e)}),
                #     content_type='application/json'
                # )
        
        return render(request, self.form_template, {
            'proyecto': proyecto,
            'form': form,
        }, status=400)


# ========== UPDATE VIEW GENÉRICA ==========

class GenericUpdateView(View):
    """
    Vista genérica para actualizar items.
    
    Atributos requeridos:
        - model: Clase del modelo
        - service_update_function: Función del servicio para actualizar
        - row_template: Template de la fila (para reemplazar)
    """
    
    model = None
    service_update_function = None
    row_template = None
    form_class = None
    
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['PUT']))
    def put(self, request, item_id, **kwargs):
        """PUT: Actualiza un item y retorna su fila HTML."""
        from django.http import QueryDict
        
        try:
            data = QueryDict(request.body)
            service_func = self.__class__.service_update_function
            item = service_func(item_id, data)
            singular = self.model._meta.model_name if self.model is not None else 'item'
            context = {'item': item, singular: item}
            
            if self.form_class:
                kwargs = {}
                sig = inspect.signature(self.form_class.__init__)
                if 'proyecto' in sig.parameters:
                    if hasattr(item, 'proyecto') and item.proyecto:
                        kwargs['proyecto'] = item.proyecto
                context['form'] = self.form_class(**kwargs)
            
            response = render(request, self.row_template, context)
            response['HX-Trigger'] = f'item-updated:{item.id}'
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}),
                content_type='application/json'
            )


# ========== DELETE VIEW GENÉRICA ==========

class GenericDeleteView(View):
    """
    Vista genérica para eliminar items.
    
    Atributos requeridos:
        - model: Clase del modelo
        - service_delete_function: Función del servicio para eliminar
    """
    
    model = None
    service_delete_function = None
    
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['DELETE']))
    def delete(self, request, item_id, **kwargs):
        """DELETE: Elimina un item."""
        try:
            service_func = self.__class__.service_delete_function
            service_func(item_id)
            return HttpResponse(status=204)
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({'error': str(e)}),
                content_type='application/json'
            )


# ========== BULK UPDATE VIEW GENÉRICA ==========

class GenericBulkUpdateView(View):
    """
    Vista genérica para actualizar múltiples items en lote.
    
    Atributos requeridos:
        - service_bulk_update: Función del servicio para actualizar en lote
    """
    
    service_bulk_update = None
    
    @method_decorator(login_required)
    @method_decorator(require_http_methods(['POST']))
    def post(self, request, proyecto_id):
        """POST: Actualiza múltiples items."""
        try:
            data_list = json.loads(request.body)
            service_func = self.__class__.service_bulk_update
            updated_ids = service_func(data_list)
            return JsonResponse({
                'success': True,
                'updated_count': len(updated_ids),
                'updated_ids': updated_ids
            })
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
