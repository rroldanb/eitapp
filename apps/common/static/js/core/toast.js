/**
 * Sistema de notificaciones toast desacoplado.
 * Uso: showToast('mensaje') / showToast('error', false, 5000)
 * No requiere dependencias externas.
 */
(function () {
  window.showToast = function (message, isSuccess, duration) {
    if (isSuccess === undefined) isSuccess = true;
    if (duration === undefined) duration = 3000;
    const toast = document.createElement('div');
    toast.className = 'toast-notification ' + (isSuccess ? 'toast-success' : 'toast-error');
    toast.textContent = message;
    toast.setAttribute('role', 'status');
    toast.setAttribute('aria-live', 'polite');
    document.body.appendChild(toast);
    requestAnimationFrame(function () {
      toast.classList.add('show');
    });
    setTimeout(function () {
      toast.classList.remove('show');
      setTimeout(function () {
        toast.remove();
      }, 300);
    }, duration);
  };
})();
