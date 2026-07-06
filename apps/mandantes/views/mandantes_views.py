from django.contrib.auth.decorators import login_required
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render

from apps.mandantes.forms import ContactoForm, MandanteForm
from apps.mandantes.models import Contacto, Mandante
from apps.mandantes.services.mandantes_service import *


@login_required
def mandantes_view(request: HttpRequest) -> HttpResponse:
    mandantes = get_all_mandantes()
    return render(request, "mandantes.html", {"mandantes": mandantes, "list_title": "Mandantes"})


def mandante_detail_view(request: HttpRequest, mandante_id: str) -> HttpResponse:
    # task = Task.objects.get(id=task_id)
    mandante = get_object_or_404(Mandante, id=mandante_id)
    if request.method == "GET":
        # task = get_object_or_404(Task, id=task_id)
        form = MandanteForm(instance=mandante)
        return render(
            request,
            "mandante_detail.html",
            {"mandante": mandante, "contactos": mandante.contactos.all(), "form": form},
        )
    else:
        try:
            form = MandanteForm(request.POST, instance=mandante)
            if form.is_valid():
                form.save()
                return redirect("mandantes")
        except Exception as e:
            return render(
                request,
                "mandante_detail.html",
                {"mandante": mandante, "form": form, "error": str(e)},
            )


def mandante_create_view(request: HttpRequest) -> HttpResponse:
    if request.method == "GET":
        return render(request, "mandante_create.html", {"form": MandanteForm})
    else:
        try:
            form = MandanteForm(request.POST)
            new_mandante = form.save(commit=False)
            new_mandante.save()
            return redirect("mandantes")
        except Exception as e:
            return render(request, "mandante_create.html", {"form": form, "error": str(e)})


def mandante_delete_view(request: HttpRequest, mandante_id: str) -> HttpResponse:
    if request.method == "POST":
        mandante_delete(mandante_id)
    return redirect("mandantes")


def contactos_view(request: HttpRequest, mandante_id: str) -> HttpResponse:
    contactos = get_contactos_by_mandante(mandante_id)
    mandante = get_object_or_404(Mandante, id=mandante_id)
    return render(
        request,
        "contactos.html",
        {"contactos": contactos, "mandante": mandante, "list_title": "Contactos"},
    )


def contacto_detail_view_base(request: HttpRequest, contacto_id: str) -> HttpResponse:
    contacto = get_contacto_by_id(contacto_id)
    return render(request, "contacto_detail.html", {"contacto": contacto})


def contacto_detail_view(request: HttpRequest, contacto_id: str) -> HttpResponse:
    contacto = get_object_or_404(Contacto, id=contacto_id)
    if request.method == "GET":
        form = ContactoForm(instance=contacto)
        return render(request, "contacto_detail.html", {"contacto": contacto, "form": form})
    else:
        try:
            form = ContactoForm(request.POST, instance=contacto)
            if form.is_valid():
                form.save()
                return redirect("mandantes")
        except Exception as e:
            return render(
                request,
                "contacto_detail.html",
                {"contacto": contacto, "form": form, "error": str(e)},
            )


def contacto_delete_view(request: HttpRequest, contacto_id: str) -> HttpResponse:
    if request.method == "POST":
        contacto = get_contacto_by_id(contacto_id)
        contacto.delete()
    return redirect("mandantes")


def contacto_create_view(request: HttpRequest, mandante_id: str) -> HttpResponse:
    mandante = get_object_or_404(Mandante, id=mandante_id)

    if request.method == "POST":
        form = ContactoForm(request.POST)
        if form.is_valid():
            contacto = form.save(commit=False)
            contacto.mandante = mandante
            contacto.save()
            return redirect("mandante_detail", mandante_id=mandante.id)
    else:
        form = ContactoForm()

    return render(request, "contacto_create.html", {"form": form, "mandante": mandante})
