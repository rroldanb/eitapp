from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render

from apps.red_vial.forms.coeficiente_cruce_form import CoeficienteCruceForm
from apps.red_vial.services.red_vial_service import (
    coeficiente_create,
    get_all_coeficientes,
)


@login_required
def coeficientes_list_view(request: HttpRequest) -> HttpResponse:
    coeficientes = get_all_coeficientes()
    return render(request, "red_vial/coeficientes_list.html", {"coeficientes": coeficientes})


@login_required
def coeficiente_create_view(request: HttpRequest) -> HttpResponse:
    if request.method == "POST":
        form = CoeficienteCruceForm(request.POST)
        if form.is_valid():
            coeficiente_create(form.cleaned_data)
            return redirect("coeficientes_list")
    else:
        form = CoeficienteCruceForm()
    return render(request, "red_vial/coeficiente_form.html", {"form": form})
