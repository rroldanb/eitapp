import contextlib
import io
import uuid
from typing import Any

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from PIL import Image, UnidentifiedImageError


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

    filename = f"proyectos/{uuid.uuid4()}.webp"
    buffer = io.BytesIO()
    img.save(buffer, format="WebP", quality=92, method=6)
    saved = default_storage.save(filename, ContentFile(buffer.getvalue()))
    return default_storage.url(saved)


def delete_project_image(image_url: str | None) -> None:
    if not image_url:
        return
    media_url = settings.MEDIA_URL
    if media_url not in image_url:
        return
    path = image_url.split(media_url, 1)[1].lstrip("/")
    if not path:
        return
    with contextlib.suppress(Exception):
        default_storage.delete(path)


upload_image = upload_project_image
delete_image = delete_project_image
