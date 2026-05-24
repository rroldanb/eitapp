import base64
from django.core.files.base import ContentFile


MAX_SIZE = 5 * 1024 * 1024  # 5MB


def get_image_from_request(request):
    """
    Retorna un archivo listo para subir a Supabase
    desde base64 (paste) o request.FILES
    """

    image_data = request.POST.get("image_file")

    if image_data:
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
        pass

    image = request.FILES.get("image")

    if image:
        if image.size > MAX_SIZE:
            raise ValueError("Archivo muy grande (máx 5MB)")

        return image

    return None