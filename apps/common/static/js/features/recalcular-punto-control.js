(function () {
  function recalcularEnRow(row) {
    const prior = row.querySelector('[name="is_prioritario"]');
    const pistas = row.querySelector('[name="numero_pistas"]');
    const interseccion = row.querySelector('[name="interseccion"]');
    const velIni = row.querySelector('[name="vel_ini"]');
    const velMod = row.querySelector('[name="vel_mod"]');
    if (!prior || !pistas || !interseccion || !velIni || !velMod) return;
    const p = prior.checked;
    const n = parseFloat(pistas.value) || 0;
    let valInt, valVI, valVM;
    if (n > 0) {
      if (p) {
        valInt = 1800 * n;
        valVI = valInt / n / 35;
      } else {
        valInt = 700 * n;
        valVI = 35;
      }
      valVM = Math.round(valVI);
    } else {
      valInt = 0;
      valVI = 0;
      valVM = 0;
    }
    interseccion.value = valInt;
    velIni.value = valVI.toFixed(2);
    velMod.value = valVM;
  }

  const tbody = document.getElementById('puntos-control-table-body');
  if (tbody) {
    tbody.addEventListener('change', function (e) {
      const row = e.target.closest('tr.punto-control-row');
      if (
        row &&
        (e.target.matches('[name="is_prioritario"]') || e.target.matches('[name="numero_pistas"]'))
      ) {
        recalcularEnRow(row);
      }
    });
    tbody.addEventListener('input', function (e) {
      const row = e.target.closest('tr.punto-control-row');
      if (row && e.target.matches('[name="numero_pistas"]')) recalcularEnRow(row);
    });
    tbody.querySelectorAll('tr.punto-control-row').forEach(recalcularEnRow);
  }

  const form = document.getElementById('new-punto-control-form');
  if (form) {
    const priorCheck = form.querySelector('[name="is_prioritario"]');
    const pistasInput = form.querySelector('[name="numero_pistas"]');
    const interseccionInput = form.querySelector('[name="interseccion"]');
    const velIniInput = form.querySelector('[name="vel_ini"]');
    const velModInput = form.querySelector('[name="vel_mod"]');
    if (priorCheck && pistasInput) {
      const recalcularForm = function () {
        const prior = priorCheck.checked;
        const pistas = parseFloat(pistasInput.value) || 0;
        let valInt, valVI, valVM;
        if (pistas > 0) {
          if (prior) {
            valInt = 1800 * pistas;
            valVI = valInt / pistas / 35;
          } else {
            valInt = 700 * pistas;
            valVI = 35;
          }
          valVM = Math.round(valVI);
        } else {
          valInt = 0;
          valVI = 0;
          valVM = 0;
        }
        interseccionInput.value = valInt;
        velIniInput.value = valVI.toFixed(2);
        velModInput.value = valVM;
      };
      priorCheck.addEventListener('change', recalcularForm);
      pistasInput.addEventListener('input', recalcularForm);
      recalcularForm();
    }
  }
})();
