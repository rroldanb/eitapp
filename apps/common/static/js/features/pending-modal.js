(function() {
  window.closePendingModal = function() {
    var el = document.getElementById('pending-tasks-modal');
    if (el) { el.classList.add('hidden'); document.body.style.overflow = ''; }
  };
  document.addEventListener('DOMContentLoaded', function() {
    var el = document.getElementById('pending-tasks-modal');
    if (el) { el.classList.remove('hidden'); document.body.style.overflow = 'hidden'; }
  });
  document.addEventListener('keydown', function(e) {
    if (e.key === 'Escape') closePendingModal();
  });
})();
