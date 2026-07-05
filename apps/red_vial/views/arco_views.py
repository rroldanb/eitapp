import json
from typing import Any

from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.db.models import QuerySet
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import ListView

from apps.proyectos.models import Proyecto
from apps.red_vial.forms.arco_form import ArcoForm
from apps.red_vial.models import Arco
from apps.red_vial.services.arco_service import (
    create_arco,
    delete_arco,
    get_arcos_by_proyecto,
    update_arco,
)


class ArcosListView(ListView):
    model: type = Arco
    context_object_name: str = "arcos"
    template_name: str = "red_vial/arcos_list.html"
    paginate_by: int = 20
    sort_fields: list[str] = ["codigo_arco", "origen", "destino", "longitud"]
    default_sort: str = "codigo_arco"

    @method_decorator(login_required)
    def dispatch(self, *args: Any, **kwargs: Any) -> HttpResponse:
        return super().dispatch(*args, **kwargs)

    def get_queryset(self) -> QuerySet[Arco]:
        sort_by = self.request.GET.get("sort_by", self.default_sort)
        sort_order = self.request.GET.get("sort_order", "asc")
        if sort_by not in self.sort_fields:
            sort_by = self.default_sort
        return get_arcos_by_proyecto(self.kwargs["proyecto_id"], sort_by=sort_by, order=sort_order)

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        ctx = super().get_context_data(**kwargs)
        ctx["proyecto"] = get_object_or_404(Proyecto, id=self.kwargs["proyecto_id"])
        ctx["sort_by"] = self.request.GET.get("sort_by", self.default_sort)
        ctx["sort_order"] = self.request.GET.get("sort_order", "asc")
        ctx["sort_fields"] = self.sort_fields
        return ctx

    def render_to_response(self, context: dict[str, Any], **response_kwargs: Any) -> HttpResponse:
        if self.request.headers.get("HX-Request"):
            return render(self.request, "partials/Arcos/arcos_table.html", context)
        return super().render_to_response(context, **response_kwargs)


class ArcoCreateView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(["POST"]))
    def post(self, request, proyecto_id):
        proyecto = get_object_or_404(Proyecto, id=proyecto_id)
        form = ArcoForm(request.POST, proyecto=proyecto)
        if form.is_valid():
            try:
                with transaction.atomic():
                    arco = create_arco(proyecto, form.cleaned_data)
                response = render(
                    request,
                    "partials/Arcos/arco_row.html",
                    {
                        "arco": arco,
                        "proyecto": proyecto,
                        "nodos": proyecto.nodos.all(),
                    },
                )
                response["HX-Trigger"] = "arco-created"
                return response
            except (ValidationError, IntegrityError) as e:
                form.add_error(None, str(e))
                response = render(
                    request,
                    "partials/Arcos/arco_create.html",
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
            "partials/Arcos/arco_create.html",
            {
                "proyecto": proyecto,
                "form": form,
            },
            status=400,
        )
        response["HX-Reswap"] = "outerHTML"
        return response


class ArcoUpdateView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(["PUT"]))
    def put(self, request, item_id):
        from django.http import QueryDict

        try:
            data = QueryDict(request.body)
            with transaction.atomic():
                arco = update_arco(item_id, data)
            response = render(
                request,
                "partials/Arcos/arco_row.html",
                {
                    "arco": arco,
                    "proyecto": arco.proyecto,
                    "nodos": arco.proyecto.nodos.all(),
                },
            )
            response["HX-Trigger"] = "item-updated"
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({"error": str(e)}), content_type="application/json"
            )


class ArcoDeleteView(View):
    @method_decorator(login_required)
    @method_decorator(require_http_methods(["DELETE"]))
    def delete(self, request, item_id):
        try:
            with transaction.atomic():
                delete_arco(item_id)
            response = HttpResponse(status=204)
            response["HX-Trigger"] = "arco-deleted"
            return response
        except ValidationError as e:
            return HttpResponseBadRequest(
                json.dumps({"error": str(e)}), content_type="application/json"
            )
