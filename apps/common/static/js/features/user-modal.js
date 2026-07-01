(function () {
  window.openCreateModal = function () {
    document.getElementById('create-modal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    document.getElementById('modal-username').focus();
  };
  window.closeCreateModal = function () {
    document.getElementById('create-modal').classList.add('hidden');
    document.body.style.overflow = '';
  };
  window.openPasswordModal = function (userId, username) {
    document.getElementById('password-modal-user').textContent = username;
    document.getElementById('password-form').action = '/usuarios/' + userId + '/change-password/';
    document.getElementById('password-modal').classList.remove('hidden');
    document.body.style.overflow = 'hidden';
    document.getElementById('modal-new-password1').focus();
  };
  window.closePasswordModal = function () {
    document.getElementById('password-modal').classList.add('hidden');
    document.body.style.overflow = '';
  };
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeCreateModal();
      closePasswordModal();
    }
  });
})();
