(function() {
  window.toggleDestino = function() {
    var val = document.querySelector('input[name="destino_tipo"]:checked');
    if (!val) return;
    document.getElementById('destino_existente').classList.toggle('hidden', val.value !== 'existente');
    document.getElementById('destino_nuevo').classList.toggle('hidden', val.value !== 'nuevo');
  };

  window.toggleMandante = function() {
    var val = document.querySelector('input[name="mandante_tipo"]:checked');
    if (!val) return;
    document.getElementById('mandante_existente').classList.toggle('hidden', val.value !== 'existente');
    document.getElementById('mandante_nuevo').classList.toggle('hidden', val.value !== 'nuevo');
  };

  document.addEventListener('DOMContentLoaded', function() {
    if (document.querySelector('input[name="destino_tipo"]')) toggleDestino();
    if (document.querySelector('input[name="mandante_tipo"]')) toggleMandante();
  });
})();
