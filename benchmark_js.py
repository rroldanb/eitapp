#!/usr/bin/env python3
"""Benchmark JS payload BEFORE and AFTER modularization.

Usage:
    python benchmark_js.py BEFORE    # baseline
    python benchmark_js.py AFTER     # after refactor

Output: tabular comparison per page of:
  - inline JS bytes (embedded in HTML)
  - external JS files referenced (count)
  - external JS size (sum of those file sizes)
  - total JS bytes transferred
  - note on changes
"""

import json
import os
import re
import sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "transito_backend.settings")

import django
from django.conf import settings

django.setup()

# Allow testserver for CLI-based Django test client
settings.ALLOWED_HOSTS.append("testserver")

from django.conf import settings
from django.contrib.auth.models import User
from django.test import Client

from apps.proyectos.models.proyecto import Proyecto
from apps.tasks.models.tasks import Task

client = Client()

# ---------------------------------------------------------------------------
# Login as existing user
# ---------------------------------------------------------------------------
try:
    u = User.objects.filter(is_superuser=True).first() or User.objects.first()
    LOGGED_USER = u.username if u else "none"
except Exception as e:
    LOGGED_USER = f"ERROR: {e}"

# ---------------------------------------------------------------------------
# Pages to benchmark
# ---------------------------------------------------------------------------
PAGES = []

# Home (anonymous) — log out first
PAGES.append(("LOGOUT_THEN_GET", "/", {}, "home (anon)"))

# Authenticated pages
PAGES.append(("GET", "/", {}, "home (auth)"))

# Admin
PAGES.append(("GET", "/admin/backup-db/", {}, "backup"))
PAGES.append(("GET", "/admin/restore-db/", {}, "restore"))
PAGES.append(("GET", "/admin/migracion/", {}, "migracion_gui"))

# Users
PAGES.append(("GET", "/usuarios/", {}, "user_management"))

# Projects
PAGES.append(("GET", "/proyectos/", {}, "proyectos_list"))
proyecto = Proyecto.objects.first()
if proyecto:
    PAGES.append(("GET", f"/proyectos/{proyecto.id}/", {}, "proyecto_detail"))

# Tasks
PAGES.append(("GET", "/tasks/", {}, "task_list"))
task = Task.objects.first()
if task:
    PAGES.append(("GET", f"/tasks/{task.id}/", {}, "task_detail"))

# Red Vial
from apps.red_vial.models.nodo import Nodo

nodo = Nodo.objects.first()
if proyecto:
    PAGES.append(("GET", f"/red-vial/proyecto/{proyecto.id}/puntos-control/", {}, "puntos_control"))
    PAGES.append(("GET", f"/red-vial/proyecto/{proyecto.id}/nodos/", {}, "nodos_list"))

if proyecto:
    PAGES.append(
        ("GET", f"/red-vial/proyecto/{proyecto.id}/analisis-flujos/", {}, "analisis_flujos")
    )

if proyecto:
    PAGES.append(("GET", f"/red-vial/proyecto/{proyecto.id}/importar/", {}, "import_start"))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

STATIC_DIRS = [
    os.path.join(settings.BASE_DIR, "apps", "common", "static"),
    os.path.join(settings.BASE_DIR, "theme", "static"),
]

KNOWN_STATIC_PREFIXES = ["/static/", "/theme/"]


def get_static_file_size(src_url):
    """Resolve a static URL to filesystem path and return file size."""
    # Strip known prefixes
    path = src_url
    for prefix in KNOWN_STATIC_PREFIXES:
        if path.startswith(prefix):
            path = path[len(prefix) :]
            break

    # Try each static dir
    for sd in STATIC_DIRS:
        full = os.path.normpath(os.path.join(sd, path))
        if os.path.isfile(full):
            return os.path.getsize(full)

    # Fallback: walk by basename
    basename = os.path.basename(path)
    for root, _dirs, files in os.walk(settings.BASE_DIR):
        if basename in files:
            return os.path.getsize(os.path.join(root, basename))

    # CDN URLs — log them
    if src_url.startswith("http"):
        return 0  # can't measure external CDN

    return 0


def extract_scripts(html):
    """Return list of {'type': 'inline'|'external', 'src': ..., 'content': ..., 'bytes': ...}"""
    scripts = []
    # Regex to find script tags
    pattern = re.compile(r"<script\b([^>]*?)>(.*?)</script>", re.DOTALL | re.IGNORECASE)
    for match in pattern.finditer(html):
        attrs = match.group(1)
        content = match.group(2).strip()
        src_match = re.search(r'src=["\']([^"\']+)["\']', attrs)
        if src_match:
            src = src_match.group(1)
            # Resolve static
            fsize = get_static_file_size(src)
            scripts.append(
                {
                    "type": "external",
                    "src": src,
                    "content": "",
                    "bytes": fsize,
                }
            )
        elif content and not re.match(r"^\s*$", content):
            b = len(content.encode("utf-8"))
            scripts.append(
                {
                    "type": "inline",
                    "src": "",
                    "content": content[:100],
                    "bytes": b,
                }
            )
    return scripts


def benchmark_page(method, path, data, label):
    if method == "LOGOUT_THEN_GET":
        client.logout()
        resp = client.get(path, data=data, follow=True)
    elif method == "GET":
        client.force_login(u)
        resp = client.get(path, data=data, follow=True)
    else:
        resp = client.post(path, data=data, follow=True)
    html = resp.content.decode("utf-8")
    scripts = extract_scripts(html)

    inline_bytes = sum(s["bytes"] for s in scripts if s["type"] == "inline")
    external_count = sum(1 for s in scripts if s["type"] == "external")
    external_bytes = sum(s["bytes"] for s in scripts if s["type"] == "external")
    total_js = inline_bytes + external_bytes
    total_scripts = len(scripts)

    return {
        "label": label,
        "status": resp.status_code,
        "inline_scripts": sum(1 for s in scripts if s["type"] == "inline"),
        "inline_bytes": inline_bytes,
        "external_count": external_count,
        "external_bytes": external_bytes,
        "total_js_bytes": total_js,
        "total_scripts": total_scripts,
    }


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------
phase = sys.argv[1] if len(sys.argv) > 1 else "BEFORE"
results = []
for method, path, data, label in PAGES:
    try:
        r = benchmark_page(method, path, data, label)
        results.append(r)
    except Exception as e:
        results.append(
            {
                "label": label,
                "status": f"ERR: {e}",
                "inline_scripts": 0,
                "inline_bytes": 0,
                "external_count": 0,
                "external_bytes": 0,
                "total_js_bytes": 0,
                "total_scripts": 0,
            }
        )

# ---------------------------------------------------------------------------
# Report
# ---------------------------------------------------------------------------
print(f"{'=' * 80}")
print(f"  JS BENCHMARK — {phase}")
print(f"  Logged in as: {LOGGED_USER}")
print(f"{'=' * 80}")
print("")
print(f"{'Page':<28} {'Status':<8} {'Inline':<8} {'Ext refs':<10} {'Ext KB':<10} {'Total KB':<10}")
print(f"{'-' * 28} {'-' * 8} {'-' * 8} {'-' * 10} {'-' * 10} {'-' * 10}")

total_inline = 0
total_ext_refs = 0
total_ext_bytes = 0
total_js = 0

for r in results:
    inline_kb = r["inline_bytes"] / 1024
    ext_kb = r["external_bytes"] / 1024
    total_kb = r["total_js_bytes"] / 1024
    print(
        f"{r['label']:<28} {r['status']!s:<8} {inline_kb:<8.1f} {r['external_count']:<10} {ext_kb:<10.1f} {total_kb:<10.1f}"
    )
    total_inline += r["inline_bytes"]
    total_ext_refs += r["external_count"]
    total_ext_bytes += r["external_bytes"]
    total_js += r["total_js_bytes"]

print(f"{'-' * 28} {'-' * 8} {'-' * 8} {'-' * 10} {'-' * 10} {'-' * 10}")
total_inline_kb = total_inline / 1024
total_ext_kb = total_ext_bytes / 1024
total_js_kb = total_js / 1024
avg_refs = total_ext_refs / len(results) if results else 0
print(
    f"{'TOTAL / AVG':<28} {'':<8} {total_inline_kb:<8.1f} {avg_refs:<10.1f} {total_ext_kb:<10.1f} {total_js_kb:<10.1f}"
)
print("")

# Summary
print("Summary:")
print(f"  Pages sampled:     {len(results)}")
print(f"  Total inline JS:   {total_inline_kb:.1f} KB")
print(f"  Avg ext refs/page: {avg_refs:.1f}")
print(f"  Total JS payload:  {total_js_kb:.1f} KB")
print("")

# Save for diff
out = {
    "phase": phase,
    "logged_as": LOGGED_USER,
    "results": results,
    "summary": {
        "pages": len(results),
        "total_inline_kb": round(total_inline_kb, 1),
        "avg_ext_refs": round(avg_refs, 1),
        "total_js_kb": round(total_js_kb, 1),
    },
}
with open(f"/tmp/benchmark_{phase.lower()}.json", "w") as f:
    json.dump(out, f, indent=2, default=str)
print(f"Saved to: /tmp/benchmark_{phase.lower()}.json")
