from django.shortcuts import render
from django.contrib.auth.decorators import login_required


def base_view(request):
    """Renderiza el template base.html para verificar Tailwind CSS"""
    return render(request, 'base.html')
