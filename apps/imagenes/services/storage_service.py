import uuid
import io
import os
from PIL import Image
from apps.imagenes.utils.supabase_client import supabase

BUCKET = os.getenv("SUPABASE_BUCKET")


def upload_project_image(file):
    try:
        img = Image.open(file)
    except Exception as e:
        raise Exception(f"Error abriendo imagen: {str(e)}")

    if img.mode in ('RGBA', 'LA', 'P'):
        img = img.convert('RGBA')
        background = Image.new('RGBA', img.size, (255, 255, 255))
        img = Image.alpha_composite(background, img)
    img = img.convert('RGB')

    webp_buffer = io.BytesIO()
    img.save(webp_buffer, format='WebP', quality=92, method=6)
    webp_buffer.seek(0)

    file_name = f"{uuid.uuid4()}.webp"

    try:
        supabase.storage.from_(BUCKET).upload(
            file_name,
            webp_buffer.read(),
            {"content-type": "image/webp"}
        )
    except Exception as e:
        raise Exception(f"Error subiendo imagen a Supabase: {str(e)}")

    public_url = supabase.storage.from_(BUCKET).get_public_url(file_name)
    return public_url


def delete_project_image(image_url):
    try:
        file_name = image_url.rstrip('/').rsplit('/', 1)[-1]
        supabase.storage.from_(BUCKET).remove([file_name])
    except Exception as e:
        raise Exception(f"Error eliminando imagen de Supabase: {str(e)}")


upload_image = upload_project_image
delete_image = delete_project_image
