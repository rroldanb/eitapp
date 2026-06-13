(function() {
  var modal = document.getElementById('delete-modal');
  if (!modal) return;
  var projectName = modal.dataset.projectName || '';

  window.openDeleteModal = function() {
    modal.classList.remove('hidden');
    var input = document.getElementById('confirm-name-input');
    if (input) { input.value = ''; }
    var btn = document.getElementById('confirm-delete-btn');
    if (btn) {
      btn.disabled = true;
      btn.classList.add('opacity-50', 'cursor-not-allowed');
      btn.classList.remove('opacity-100', 'cursor-pointer');
    }
    document.body.style.overflow = 'hidden';
  };

  window.closeDeleteModal = function() {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
  };

  window.onConfirmNameChange = function(input) {
    var btn = document.getElementById('confirm-delete-btn');
    if (!btn) return;
    if (input.value === projectName) {
      btn.disabled = false;
      btn.classList.remove('opacity-50', 'cursor-not-allowed');
      btn.classList.add('opacity-100', 'cursor-pointer');
    } else {
      btn.disabled = true;
      btn.classList.add('opacity-50', 'cursor-not-allowed');
      btn.classList.remove('opacity-100', 'cursor-pointer');
    }
  };

  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closeDeleteModal();
  });

  modal.addEventListener('click', function(e) {
    if (e.target === this) closeDeleteModal();
  });
})();
