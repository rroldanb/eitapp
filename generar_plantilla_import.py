#!/usr/bin/env python3
"""Genera plantilla Excel de importacion con una hoja por tabla."""

from apps.common.utils.excel_utils import generar_plantilla

wb = generar_plantilla()

default_name = "plantilla_importacion_eitapp.xlsx"

try:
    import tkinter as tk
    from tkinter import filedialog
    root = tk.Tk()
    root.withdraw()
    root.call("wm", "attributes", ".", "-topmost", True)
    output_path = filedialog.asksaveasfilename(
        title="Guardar plantilla de importación",
        defaultextension=".xlsx",
        filetypes=[("Excel files", "*.xlsx")],
        initialfile=default_name,
    )
    root.destroy()
    if not output_path:
        print("❌ Guardado cancelado por el usuario.")
        exit(0)
except Exception:
    output_path = input(f"📁 Ruta de guardado (Enter para default: ./{default_name}): ").strip()
    if not output_path:
        output_path = default_name
    if not output_path.endswith(".xlsx"):
        output_path += ".xlsx"

wb.save(output_path)
print(f"✅ Plantilla generada: {output_path}")
print(f"   Hojas: {len(wb.sheetnames)} → {', '.join(wb.sheetnames)}")
