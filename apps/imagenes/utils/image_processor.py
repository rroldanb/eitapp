import base64
from django.core.files.base import ContentFile


MAX_SIZE = 5 * 1024 * 1024  # 5MB


def get_image_from_request(request):
    """
    Retorna un archivo listo para subir a Supabase
    desde base64 (paste) o request.FILES
    """

    # 🔹 Caso 1: imagen desde portapapeles
    image_data = request.POST.get("image_file")

    if image_data:
        print("Procesando imagen pegada...")
        print(f"Data recibida: {image_data[:30]}...")  # Debug: muestra el inicio del string
        try:
            format, imgstr = image_data.split(';base64,')
            ext = format.split('/')[-1]

            file = ContentFile(
                base64.b64decode(imgstr),
                name=f"paste.{ext}"
            )

            if file.size > MAX_SIZE:
                raise ValueError("Imagen muy grande (máx 5MB)")

            return file

        except Exception:
            raise ValueError("Error procesando imagen pegada")
    else:
        print("No se encontró imagen pegada en el formulario.")
    # 🔹 Caso 2: archivo tradicional
    image = request.FILES.get("image")

    if image:
        if image.size > MAX_SIZE:
            raise ValueError("Archivo muy grande (máx 5MB)")

        return image

    return None