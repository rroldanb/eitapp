(function () {
  const backupForm = document.getElementById('backup-form');
  if (!backupForm) return;

  const backupNameInput = document.getElementById('backup_name');
  const spinner = document.getElementById('submit-spinner');
  const feedback = document.getElementById('backup-feedback');

  function clearFeedback() {
    if (!feedback) return;
    feedback.className = 'hidden rounded-lg p-4 text-sm';
    feedback.textContent = '';
  }

  function showFeedback(message, type) {
    if (!feedback) return;
    feedback.textContent = message;
    feedback.className = 'rounded-lg p-4 text-sm';
    if (type === 'success') {
      feedback.classList.add('bg-emerald-50', 'border', 'border-emerald-200', 'text-emerald-800');
    } else {
      feedback.classList.add('bg-red-50', 'border', 'border-red-200', 'text-red-800');
    }
  }

  backupForm.addEventListener('submit', async function (event) {
    event.preventDefault();
    clearFeedback();
    const backupName = backupNameInput.value.trim();
    if (!backupName) {
      showToast('Debes indicar el nombre del archivo de respaldo.', false);
      backupNameInput.focus();
      return;
    }
    spinner.style.display = 'inline-flex';
    const submitButton = backupForm.querySelector('button[type="submit"]');
    submitButton.setAttribute('disabled', 'disabled');
    try {
      const formData = new FormData(backupForm);
      const response = await fetch(backupForm.action || window.location.href, {
        method: 'POST',
        body: formData,
        credentials: 'same-origin',
      });
      const contentType = response.headers.get('Content-Type') || '';
      if (!response.ok || contentType.indexOf('application/zip') === -1) {
        let message = 'Error al generar el respaldo.';
        try {
          const text = await response.text();
          if (text) {
            message =
              text
                .replace(/<[^>]*>/g, '')
                .trim()
                .slice(0, 200) || message;
          }
        } catch (ignored) {}
        throw new Error(message);
      }
      const blob = await response.blob();
      const filename = backupName.replace(/[^A-Za-z0-9_.-]/g, '_') + '.zip';
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = url;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      document.body.removeChild(anchor);
      URL.revokeObjectURL(url);
      showFeedback('Respaldo completado. El archivo está descargándose.', 'success');
    } catch (err) {
      showFeedback(err.message || 'No se pudo generar el respaldo.', 'error');
    } finally {
      spinner.style.display = 'none';
      if (submitButton) submitButton.removeAttribute('disabled');
    }
  });
})();
