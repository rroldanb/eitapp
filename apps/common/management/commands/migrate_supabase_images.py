import logging
import requests
from django.db import connection
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from apps.imagenes.services.storage_service import upload_project_image

logger = logging.getLogger(__name__)


def _is_supabase_url(url: str | None) -> bool:
    return url is not None and "supabase.co" in url


def _download_image(url: str) -> ContentFile:
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    filename = url.rsplit("/", 1)[-1] or "image.bin"
    return ContentFile(resp.content, name=filename)


def _find_supabase_records() -> list[tuple[str, str, str]]:
    """Return (table, field, url) for every row with a Supabase URL."""
    records: list[tuple[str, str, str]] = []
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT id, image_url FROM proyectos_proyecto "
            "WHERE image_url IS NOT NULL AND image_url != ''"
        )
        for row in cursor.fetchall():
            if _is_supabase_url(row[1]):
                records.append(("proyectos_proyecto", "image_url", row[1]))

        cursor.execute(
            "SELECT id, imagen FROM red_vial_nodo "
            "WHERE imagen IS NOT NULL AND imagen != ''"
        )
        for row in cursor.fetchall():
            if _is_supabase_url(row[1]):
                records.append(("red_vial_nodo", "imagen", row[1]))

        cursor.execute(
            "SELECT id, plano FROM red_vial_nodo "
            "WHERE plano IS NOT NULL AND plano != ''"
        )
        for row in cursor.fetchall():
            if _is_supabase_url(row[1]):
                records.append(("red_vial_nodo", "plano", row[1]))
    return records


def _update_url(table: str, field: str, old_url: str, new_url: str) -> int:
    """Update ALL rows where field == old_url, return rows affected."""
    with connection.cursor() as cursor:
        cursor.execute(
            f"UPDATE {table} SET {field} = %s WHERE {field} = %s",
            [new_url, old_url],
        )
        return cursor.rowcount


class Command(BaseCommand):
    help = "Migrate images from Supabase Storage to local MEDIA_ROOT"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Only list what would be migrated, without doing anything",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        records = _find_supabase_records()

        if not records:
            self.stdout.write("No Supabase images found.")
            return

        # De-duplicate by URL so we only download each file once
        seen_urls: dict[str, str] = {}  # old_url -> description
        for table, field, url in records:
            if url not in seen_urls:
                seen_urls[url] = f"[{table}.{field}]"

        self.stdout.write(f"Found {len(records)} row(s) ({len(seen_urls)} unique file(s)):")
        for url, label in seen_urls.items():
            self.stdout.write(f"  {label}: {url}")

        if dry_run:
            self.stdout.write(self.style.WARNING("\nDry-run — no changes made."))
            return

        self.stdout.write("")
        migrated = 0
        errors = []

        for old_url in seen_urls:
            try:
                file = _download_image(old_url)
                new_url = upload_project_image(file)

                affected = 0
                for table, field, row_url in records:
                    if row_url == old_url:
                        affected += _update_url(table, field, old_url, new_url)

                self.stdout.write(
                    f"  OK  {new_url} ({affected} row(s) updated)"
                )
                migrated += 1
            except Exception as e:
                errors.append(f"{old_url}: {e}")
                self.stdout.write(self.style.ERROR(f"  ERR {old_url}: {e}"))

        self.stdout.write(f"\nMigrated: {migrated}/{len(seen_urls)} file(s)")
        if errors:
            self.stdout.write(self.style.ERROR(f"Errors: {len(errors)}"))
            for err in errors:
                self.stdout.write(self.style.ERROR(f"  - {err}"))
        else:
            self.stdout.write(self.style.SUCCESS("All OK"))
