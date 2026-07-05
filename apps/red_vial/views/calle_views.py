import json
from typing import Any

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.http import HttpRequest, HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView

from apps.proyectos.models import Proyecto
from apps.red_vial.forms.calle_form import CalleForm
from apps.red_vial.models import Calle
from apps.red_vial.services.calle_service import (
    create_calle,
    delete_calle,
    get_calles_by_proyecto,
    update_calle,
)


class CalleListView(ListView):
    model: type = Calle
    context_object_name: str = "calles"
    template_name: str = "red_vial/calles_list.html"
    paginate_by: int = 20
    sort_fields: list[str] = ["numero", "nombre", "nodos"]
    default_sort: str = "numero"

    @method_decorator(login_required)
    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(*args, **kwargs)

    def get_queryset(self) -> QuerySet[Calle]:
        sort_by = self.request.GET.get("sort_by", self.default_sort)
        sort_order = self.request.GET.get("sort_order", "asc")
        if sort_by not in self.sort_fields:
            sort_by = self.default_sort
        return get_calles_by_proyecto(self.kwargs["proyecto_id"], sort_by=sort_by, order=sort_order)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["proyecto"] = get_object_or_404(Proyecto, id=self.kwargs["proyecto_id"])
        ctx["sort_by"] = self.request.GET.get("sort_by", self.default_sort)
        ctx["sort_order"] = self.request.GET.get("sort_order", "asc")
        ctx["sort_fields"] = self.sort_fields
        return ctx

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if self.request.headers.get("HX-Request"):
            return render(self.request, "partials/Calles/calles_table.html", context)
        return super().render_to_response(context, **response_kwargs)


class CalleCreateView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(["POST"]))
    def post(self, request: HttpRequest, proyecto_id: str) -> HttpResponse:
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        form = CalleForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            try:
                with transaction.atomic():
                    calle = create_calle(proyecto, form.cleaned_data)
                response = render(
                    request,
                    "partials/Calles/calle_row.html",
                    {
                        "calle": calle,
                        "proyecto": proyecto,
                    },
                )
                response["HX-Trigger"] = "calle-created"
                return response
            except (ValidationError, IntegrityError) as e:
                form.add_error(None, str(e))
                response = render(
                    request,
                    "partials/Calles/calle_create.html",
                    {
                        "proyecto": proyecto,
                        "form": form,
                    },
                    status=400,
                )
                response["HX-Reswap"] = "outerHTML"
                return response
        response = render(
            request,
            "partials/Calles/calle_create.html",
            {
                "proyecto": proyecto,
                "form": form,
            },
            status=400,
        )
        response["HX-Reswap"] = "outerHTML"
        return response


class CalleUpdateView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(["PUT"]))
    def put(self, request: HttpRequest, item_id: str) -> HttpResponse:
        from django.http import QueryDict

        try:
            data = QueryDict(request.body)
            with transaction.atomic():
                calle = update_calle(item_id, data)
            response = render(
                request,
                "partials/Calles/calle_row.html",
                {
                    "calle": calle,
                    "proyecto": calle.proyecto,
                },
            )
            response["HX-Trigger"] = "item-updated"
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({"error": str(e)}), content_type="application/json"
            )


class CalleDeleteView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(["DELETE"]))
    def delete(self, request: HttpRequest, item_id: str) -> HttpResponse:
        try:
            with transaction.atomic():
                delete_calle(item_id)
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "calle-deleted"
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({"error": str(e)}), content_type="application/json"
            )
