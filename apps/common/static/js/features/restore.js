(function () {
  const restoreForm = document.getElementById('restore-form');
  if (!restoreForm) return;

  restoreForm.addEventListener('submit', function (e) {
    const fileInput = document.getElementById('backup_file');
    if (!fileInput || !fileInput.files.length) {
      showToast('Debes seleccionar un archivo ZIP antes de restaurar.', false);
      e.preventDefault();
      return;
    }
    const btn = document.getElementById('restore-submit-btn');
    btn.disabled = true;
    btn.innerHTML = '<i class="fas fa-spinner fa-spin mr-1"></i> Restaurando...';
  });
})();
