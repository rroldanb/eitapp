from apps.mandantes.services.mandantes_service import *
from apps.mandantes.forms import MandanteForm, ContactoForm
from apps.mandantes.models import Mandante, Contacto
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required



@login_required
def mandantes_view(request):
    mandantes = get_all_mandantes()
    # print(mandantes)
    return render(request, "mandantes.html", {
        "mandantes": mandantes,
        "list_title": "Mandantes"
    })



def mandante_detail_view(request, mandante_id):
    #task = Task.objects.get(id=task_id)
    mandante = get_object_or_404(Mandante, id=mandante_id)
    if request.method == 'GET':
        # task = get_object_or_404(Task, id=task_id)
        form = MandanteForm(instance=mandante)
        return render(request, 'mandante_detail.html', {
            'mandante': mandante, 
            "contactos": mandante.contactos.all(),
            'form': form})
    else:
        try:
            form = MandanteForm(request.POST, instance=mandante)
            if form.is_valid():
                form.save()
                return redirect('mandantes')
        except Exception as e:
            return render(request, 'mandante_detail.html', {'mandante': mandante, 'form': form, 'error': str(e)})



def mandante_create_view(request):
    #return render(request, 'create_task.html')
   if request.method == 'GET':
       return render(request, 'mandante_create.html', {
           'form': MandanteForm
       })
   else:
       try:
           form = MandanteForm(request.POST)
           #if form.is_valid():
           new_mandante = form.save(commit=False)
           new_mandante.save()
           return redirect('mandantes')
       except Exception as e:
           return render(request, 'mandante_create.html', {
               'form': form,
               'error': str(e)
           })

def mandante_delete_view(request, mandante_id):

    if request.method == "POST":
        mandante_delete(mandante_id)

    return redirect("mandantes")



def contactos_view(request, mandante_id):
    contactos = get_contactos_by_mandante(mandante_id)
    return render(request, "contactos.html", {
        "contactos": contactos,
        "list_title": "Contactos"
    })

def contacto_detail_view_base(request, contacto_id):
    contacto = get_contacto_by_id(contacto_id)

    return render(request, "contacto_detail.html", {
        "contacto": contacto
    })



def contacto_detail_view(request, contacto_id):
    #task = Task.objects.get(id=task_id)
    contacto = get_object_or_404(Contacto, id=contacto_id)
    if request.method == 'GET':
        # task = get_object_or_404(Task, id=task_id)
        form = ContactoForm(instance=contacto)
        return render(request, 'contacto_detail.html', {
            'contacto': contacto, 
            'form': form})
    else:
        try:
            form = ContactoForm(request.POST, instance=contacto)
            if form.is_valid():
                form.save()
                return redirect('mandantes')
        except Exception as e:
            return render(request, 'contacto_detail.html', {'contacto': contacto, 'form': form, 'error': str(e)})





def contacto_delete_view(request, contacto_id):

    if request.method == "POST":
        contacto = get_contacto_by_id(contacto_id)
        contacto.delete()

    return redirect("mandantes")


def contacto_create_view(request, mandante_id):

    mandante = Mandante.objects.get(id=mandante_id)

    if request.method == "POST":
        form = ContactoForm(request.POST)

        if form.is_valid():
            contacto = form.save(commit=False)
            contacto.mandante = mandante
            contacto.save()

            return redirect("mandante_detail", mandante_id=mandante.id)

    else:
        form = ContactoForm()

    return render(request, "contacto_create.html", {
        "form": form,
        "mandante": mandante
    })