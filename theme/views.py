from django.shortcuts import render


def base_view(request):
    """Renderiza el template base.html para verificar Tailwind CSS"""
    return render(request, "base.html")
