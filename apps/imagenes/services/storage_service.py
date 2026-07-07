import os
import uuid
from typing import Any

from django.conf import settings
from PIL import Image, UnidentifiedImageError


def _media_path(subdir: str, filename: str) -> str:
    path = os.path.join(settings.MEDIA_ROOT, subdir)
    os.makedirs(path, exist_ok=True)
    return os.path.join(path, filename)


def upload_project_image(file: Any) -> str:
    try:
        img = Image.open(file)
    except (FileNotFoundError, UnidentifiedImageError, OSError) as e:
        raise ValueError(f"Error abriendo imagen: {e!s}")

    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        background = Image.new("RGBA", img.size, (255, 255, 255))
        img = Image.alpha_composite(background, img)
    img = img.convert("RGB")

    filename = f"{uuid.uuid4()}.webp"
    file_path = _media_path("proyectos", filename)
    img.save(file_path, format="WebP", quality=92, method=6)

    return f"{settings.MEDIA_URL}proyectos/{filename}"


def delete_project_image(image_url: str | None) -> None:
    if not image_url:
        return
    if not image_url.startswith(settings.MEDIA_URL):
        return
    rel_path = image_url[len(settings.MEDIA_URL) :].lstrip("/")
    abs_path = os.path.join(settings.MEDIA_ROOT, rel_path)
    if os.path.exists(abs_path):
        os.remove(abs_path)


upload_image = upload_project_image
delete_image = delete_project_image
