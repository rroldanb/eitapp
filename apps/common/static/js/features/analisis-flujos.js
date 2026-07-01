(function () {
  document.body.addEventListener('resumenes-recalculados', function () {
    const msg = document.getElementById('recalcular-msg');
    if (msg) {
      msg.textContent =
        'Res\u00famenes recalculados correctamente. Actualiza los filtros para ver los cambios.';
      msg.className = 'text-sm text-green-600';
      setTimeout(function () {
        msg.textContent = '';
      }, 5000);
    }
  });
})();
