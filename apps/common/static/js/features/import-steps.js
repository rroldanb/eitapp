(function() {
  /* paso1_upload: show filename */
  var excelInput = document.getElementById('excel-file-input');
  if (excelInput) {
    excelInput.addEventListener('change', function() {
      var display = document.getElementById('file-name-display');
      var text = document.getElementById('file-name-text');
      var label = document.querySelector('.file-label span');
      if (this.files && this.files.length > 0) {
        text.textContent = this.files[0].name;
        if (display) display.classList.remove('hidden');
        if (label) label.textContent = 'Cambiar archivo';
      }
    });
  }

  /* paso2_configurar: toggle project/mandante fields */
  function toggleFields() {
    var p = document.querySelector('.project-mode-radio:checked');
    if (p) {
      var pc = p.closest('.space-y-3');
      if (pc) {
        var pf = pc.querySelector('.project-new-fields');
        var pe = pc.querySelector('.project-existing-fields');
        if (pf) pf.style.display = p.value === 'new' ? '' : 'none';
        if (pe) pe.style.display = p.value === 'existing' ? '' : 'none';
      }
    }
    var m = document.querySelector('.mandante-mode-radio:checked');
    if (m) {
      var mc = m.closest('.space-y-3');
      if (mc) {
        var mf = mc.querySelector('.mandante-new-fields');
        var me = mc.querySelector('.mandante-existing-fields');
        if (mf) mf.style.display = m.value === 'new' ? '' : 'none';
        if (me) me.style.display = m.value === 'existing' ? '' : 'none';
      }
    }
  }
  document.querySelectorAll('.project-mode-radio, .mandante-mode-radio').forEach(function(r) {
    r.addEventListener('change', toggleFields);
  });
  toggleFields();

  /* paso2_seleccion: checkbox presets */
  var checkboxes = document.querySelectorAll('.sheet-checkbox');
  function setAll(checked) { checkboxes.forEach(function(cb) { cb.checked = checked; }); }
  document.querySelectorAll('.btn-preset').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var action = this.getAttribute('data-action');
      if (action === 'check-all') setAll(true);
      else if (action === 'uncheck-all') setAll(false);
      else if (action === 'check-contactos') {
        setAll(false);
        document.querySelectorAll('.sheet-checkbox').forEach(function(cb) {
          if (cb.value === 'Mandante' || cb.value === 'Contacto') cb.checked = true;
        });
      } else if (action === 'check-proyecto') {
        setAll(false);
        document.querySelectorAll('.sheet-checkbox').forEach(function(cb) {
          if (cb.value !== 'Mandante' && cb.value !== 'Contacto' && cb.value !== 'Proyecto') cb.checked = true;
        });
      }
    });
  });

  /* paso3_validacion: dup radio sync + toggle details */
  document.querySelectorAll('[name^="dup_"]').forEach(function(input) {
    var name = input.name;
    if (input.type === 'radio') {
      input.addEventListener('change', function() {
        var hidden = document.querySelector('input[type="hidden"][name="' + name + '"]');
        if (hidden) hidden.value = this.value;
      });
    }
  });
  document.querySelectorAll('.dup-toggle').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var target = document.getElementById(this.dataset.target);
      if (target) {
        target.classList.toggle('hidden');
        var icon = this.querySelector('i');
        if (icon) { icon.classList.toggle('fa-chevron-right'); icon.classList.toggle('fa-chevron-down'); }
      }
    });
  });
  document.querySelectorAll('.err-toggle').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var target = document.getElementById(this.dataset.target);
      if (target) {
        target.classList.toggle('hidden');
        var icon = this.querySelector('i');
        if (icon) { icon.classList.toggle('fa-chevron-right'); icon.classList.toggle('fa-chevron-down'); }
      }
    });
  });

  /* paso5_reporte: download report + toggle rejected */
  window.downloadReport = function() {
    var lines = ['=== REPORTE DE IMPORTACION ===', '', 'Resumen:'];
    var reportEl = document.getElementById('import-report-data');
    if (!reportEl) return;
    try {
      var report = JSON.parse(reportEl.dataset.report || '{}');
      var totals = JSON.parse(reportEl.dataset.totals || '{}');
    } catch(e) { return; }
    lines.push('  Insertadas: ' + totals.inserted);
    lines.push('  Actualizadas: ' + totals.updated);
    lines.push('  Omitidas: ' + (totals.skipped || 0));
    lines.push('  Rechazadas: ' + totals.rejected);
    lines.push('');
    for (var sheet in report) {
      var sr = report[sheet];
      lines.push('--- ' + sheet + ' ---');
      lines.push('  Insertadas: ' + (sr.inserted || 0));
      lines.push('  Actualizadas: ' + (sr.updated || 0));
      lines.push('  Omitidas: ' + (sr.skipped_duplicates || 0));
      if (sr.rejected && sr.rejected.length) {
        lines.push('  Rechazadas:');
        for (var i = 0; i < sr.rejected.length; i++) {
          lines.push('    - Fila ' + (sr.rejected[i].row || '?') + ': ' + (sr.rejected[i].reason || ''));
        }
      }
      lines.push('');
    }
    lines.push('=== FIN DEL REPORTE ===');
    var blob = new Blob([lines.join('\n')], {type: 'text/plain;charset=utf-8'});
    var url = URL.createObjectURL(blob);
    var a = document.createElement('a'); a.href = url; a.download = 'reporte_importacion.txt';
    a.click(); URL.revokeObjectURL(url);
  };

  document.querySelectorAll('.rej-toggle').forEach(function(btn) {
    btn.addEventListener('click', function() {
      var target = document.getElementById(this.dataset.target);
      var icon = this.querySelector('i');
      if (target) {
        target.classList.toggle('hidden');
        icon.classList.toggle('fa-chevron-right');
        icon.classList.toggle('fa-chevron-down');
      }
    });
  });
})();
