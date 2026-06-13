/**
 * Sistema genérico de modales.
 *
 * HTML esperado:
 *   <div id="mi-modal" class="fixed inset-0 z-50 hidden" role="dialog">
 *     <div class="fixed inset-0 bg-gray-900/60 modal-backdrop"></div>
 *     <div class="fixed inset-0 flex items-center justify-center p-4">...
 *   </div>
 *
 * Expone: openModal(id), closeModal(id), ModalUtils.setupAutoClose(modalId)
 */
(function() {
  window.openModal = function(id) {
    var el = document.getElementById(id);
    if (!el) return;
    el.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  };

  window.closeModal = function(id) {
    var el = document.getElementById(id);
    if (!el) return;
    el.classList.add('hidden');
    document.body.style.overflow = '';
  };

  window.ModalUtils = {
    /**
     * Vincula cierre con Escape y clic en backdrop.
     * Llamar una vez al cargar el DOM por cada modal.
     */
    setupAutoClose: function(modalId) {
      var modal = document.getElementById(modalId);
      if (!modal) return;

      document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape') {
          var ev = new CustomEvent('modal-escape', { detail: { modalId: modalId } });
          document.dispatchEvent(ev);
          window.closeModal(modalId);
        }
      });

      modal.addEventListener('click', function(e) {
        if (e.target === this) window.closeModal(modalId);
      });
    }
  };
})();
