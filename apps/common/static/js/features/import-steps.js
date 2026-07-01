(function () {
  /* paso1_upload: show filename */
  const excelInput = document.getElementById('excel-file-input');
  if (excelInput) {
    excelInput.addEventListener('change', function () {
      const display = document.getElementById('file-name-display');
      const text = document.getElementById('file-name-text');
      const label = document.querySelector('.file-label span');
      if (this.files && this.files.length > 0) {
        text.textContent = this.files[0].name;
        if (display) display.classList.remove('hidden');
        if (label) label.textContent = 'Cambiar archivo';
      }
    });
  }

  /* paso2_configurar: toggle project/mandante fields */
  function toggleFields() {
    const p = document.querySelector('.project-mode-radio:checked');
    if (p) {
      const pc = p.closest('.space-y-3');
      if (pc) {
        const pf = pc.querySelector('.project-new-fields');
        const pe = pc.querySelector('.project-existing-fields');
        if (pf) pf.style.display = p.value === 'new' ? '' : 'none';
        if (pe) pe.style.display = p.value === 'existing' ? '' : 'none';
      }
    }
    const m = document.querySelector('.mandante-mode-radio:checked');
    if (m) {
      const mc = m.closest('.space-y-3');
      if (mc) {
        const mf = mc.querySelector('.mandante-new-fields');
        const me = mc.querySelector('.mandante-existing-fields');
        if (mf) mf.style.display = m.value === 'new' ? '' : 'none';
        if (me) me.style.display = m.value === 'existing' ? '' : 'none';
      }
    }
  }
  document.querySelectorAll('.project-mode-radio, .mandante-mode-radio').forEach(function (r) {
    r.addEventListener('change', toggleFields);
  });
  toggleFields();

  /* paso2_seleccion: checkbox presets */
  const checkboxes = document.querySelectorAll('.sheet-checkbox');
  function setAll(checked) {
    checkboxes.forEach(function (cb) {
      cb.checked = checked;
    });
  }
  document.querySelectorAll('.btn-preset').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const action = this.getAttribute('data-action');
      if (action === 'check-all') setAll(true);
      else if (action === 'uncheck-all') setAll(false);
      else if (action === 'check-contactos') {
        setAll(false);
        document.querySelectorAll('.sheet-checkbox').forEach(function (cb) {
          if (cb.value === 'Mandante' || cb.value === 'Contacto') cb.checked = true;
        });
      } else if (action === 'check-proyecto') {
        setAll(false);
        document.querySelectorAll('.sheet-checkbox').forEach(function (cb) {
          if (cb.value !== 'Mandante' && cb.value !== 'Contacto' && cb.value !== 'Proyecto')
            cb.checked = true;
        });
      }
    });
  });

  /* paso3_validacion: dup radio sync + toggle details */
  document.querySelectorAll('[name^="dup_"]').forEach(function (input) {
    const name = input.name;
    if (input.type === 'radio') {
      input.addEventListener('change', function () {
        const hidden = document.querySelector('input[type="hidden"][name="' + name + '"]');
        if (hidden) hidden.value = this.value;
      });
    }
  });
  document.querySelectorAll('.dup-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const target = document.getElementById(this.dataset.target);
      if (target) {
        target.classList.toggle('hidden');
        const icon = this.querySelector('i');
        if (icon) {
          icon.classList.toggle('fa-chevron-right');
          icon.classList.toggle('fa-chevron-down');
        }
      }
    });
  });
  document.querySelectorAll('.err-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const target = document.getElementById(this.dataset.target);
      if (target) {
        target.classList.toggle('hidden');
        const icon = this.querySelector('i');
        if (icon) {
          icon.classList.toggle('fa-chevron-right');
          icon.classList.toggle('fa-chevron-down');
        }
      }
    });
  });

  /* paso5_reporte: download report + toggle rejected */
  window.downloadReport = function () {
    const lines = ['=== REPORTE DE IMPORTACION ===', '', 'Resumen:'];
    const reportEl = document.getElementById('import-report-data');
    if (!reportEl) return;
    let report = {};
    let totals = {};
    try {
      report = JSON.parse(reportEl.dataset.report || '{}');
      totals = JSON.parse(reportEl.dataset.totals || '{}');
    } catch (e) {
      return;
    }
    lines.push('  Insertadas: ' + totals.inserted);
    lines.push('  Actualizadas: ' + totals.updated);
    lines.push('  Omitidas: ' + (totals.skipped || 0));
    lines.push('  Rechazadas: ' + totals.rejected);
    lines.push('');
    for (const sheet in report) {
      const sr = report[sheet];
      lines.push('--- ' + sheet + ' ---');
      lines.push('  Insertadas: ' + (sr.inserted || 0));
      lines.push('  Actualizadas: ' + (sr.updated || 0));
      lines.push('  Omitidas: ' + (sr.skipped_duplicates || 0));
      if (sr.rejected && sr.rejected.length) {
        lines.push('  Rechazadas:');
        for (let i = 0; i < sr.rejected.length; i++) {
          lines.push(
            '    - Fila ' + (sr.rejected[i].row || '?') + ': ' + (sr.rejected[i].reason || ''),
          );
        }
      }
      lines.push('');
    }
    lines.push('=== FIN DEL REPORTE ===');
    const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'reporte_importacion.txt';
    a.click();
    URL.revokeObjectURL(url);
  };

  document.querySelectorAll('.rej-toggle').forEach(function (btn) {
    btn.addEventListener('click', function () {
      const target = document.getElementById(this.dataset.target);
      const icon = this.querySelector('i');
      if (target) {
        target.classList.toggle('hidden');
        icon.classList.toggle('fa-chevron-right');
        icon.classList.toggle('fa-chevron-down');
      }
    });
  });
})();
