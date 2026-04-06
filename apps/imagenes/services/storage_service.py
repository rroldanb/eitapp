import uuid
import mimetypes
import os
from apps.imagenes.utils.supabase_client import supabase

BUCKET = os.getenv("SUPABASE_BUCKET")


def upload_project_image(file):

    file_extension = file.name.split('.')[-1]
    file_name = f"{uuid.uuid4()}.{file_extension}"

    # 🔹 content-type seguro
    content_type = getattr(file, "content_type", None)

    if not content_type:
        content_type, _ = mimetypes.guess_type(file.name)

    if not content_type:
        content_type = "application/octet-stream"

    try:
        # 🔥 importante: resetear puntero
        file.seek(0)

        supabase.storage.from_(BUCKET).upload(
            file_name,
            file.read(),
            {"content-type": content_type}
        )

    except Exception as e:
        raise Exception(f"Error subiendo imagen a Supabase: {str(e)}")

    # 🔹 obtener URL pública
    public_url = supabase.storage.from_(BUCKET).get_public_url(file_name)

    return public_url



def delete_project_image(file_name):
    try:
        print(f"Intentando eliminar imagen: {file_name} del bucket: {BUCKET}")
        supabase.storage.from_(BUCKET).remove([file_name])
    except Exception as e:
        raise Exception(f"Error eliminando imagen de Supabase: {str(e)}")