(function() {
  function recalcularEnRow(row) {
    var prior = row.querySelector('[name="is_prioritario"]');
    var pistas = row.querySelector('[name="numero_pistas"]');
    var interseccion = row.querySelector('[name="interseccion"]');
    var velIni = row.querySelector('[name="vel_ini"]');
    var velMod = row.querySelector('[name="vel_mod"]');
    if (!prior || !pistas || !interseccion || !velIni || !velMod) return;
    var p = prior.checked;
    var n = parseFloat(pistas.value) || 0;
    var valInt, valVI, valVM;
    if (n > 0) {
      if (p) { valInt = 1800 * n; valVI = valInt / n / 35; }
      else { valInt = 700 * n; valVI = 35; }
      valVM = Math.round(valVI);
    } else { valInt = 0; valVI = 0; valVM = 0; }
    interseccion.value = valInt;
    velIni.value = valVI.toFixed(2);
    velMod.value = valVM;
  }

  var tbody = document.getElementById('puntos-control-table-body');
  if (tbody) {
    tbody.addEventListener('change', function(e) {
      var row = e.target.closest('tr.punto-control-row');
      if (row && (e.target.matches('[name="is_prioritario"]') || e.target.matches('[name="numero_pistas"]'))) {
        recalcularEnRow(row);
      }
    });
    tbody.addEventListener('input', function(e) {
      var row = e.target.closest('tr.punto-control-row');
      if (row && e.target.matches('[name="numero_pistas"]')) recalcularEnRow(row);
    });
    tbody.querySelectorAll('tr.punto-control-row').forEach(recalcularEnRow);
  }

  var form = document.getElementById('new-punto-control-form');
  if (form) {
    var priorCheck = form.querySelector('[name="is_prioritario"]');
    var pistasInput = form.querySelector('[name="numero_pistas"]');
    var interseccionInput = form.querySelector('[name="interseccion"]');
    var velIniInput = form.querySelector('[name="vel_ini"]');
    var velModInput = form.querySelector('[name="vel_mod"]');
    if (priorCheck && pistasInput) {
      function recalcularForm() {
        var prior = priorCheck.checked;
        var pistas = parseFloat(pistasInput.value) || 0;
        var valInt, valVI, valVM;
        if (pistas > 0) {
          if (prior) { valInt = 1800 * pistas; valVI = valInt / pistas / 35; }
          else { valInt = 700 * pistas; valVI = 35; }
          valVM = Math.round(valVI);
        } else { valInt = 0; valVI = 0; valVM = 0; }
        interseccionInput.value = valInt;
        velIniInput.value = valVI.toFixed(2);
        velModInput.value = valVM;
      }
      priorCheck.addEventListener('change', recalcularForm);
      pistasInput.addEventListener('input', recalcularForm);
      recalcularForm();
    }
  }
})();
