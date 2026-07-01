(function () {
  const tabs = document.querySelectorAll('.tab-btn');
  if (!tabs.length) return;

  window.switchTab = function (tab) {
    document.querySelectorAll('.tab-content').forEach(function (el) {
      el.classList.add('hidden');
    });
    document.getElementById('tab-' + tab).classList.remove('hidden');
    document.querySelectorAll('.tab-btn').forEach(function (btn) {
      btn.classList.remove('border-indigo-600', 'text-indigo-700', 'bg-indigo-50/50');
      btn.classList.add('border-transparent', 'text-gray-500');
    });
    const activeBtn = document.querySelector('.tab-btn[data-tab="' + tab + '"]');
    activeBtn.classList.remove('border-transparent', 'text-gray-500');
    activeBtn.classList.add('border-indigo-600', 'text-indigo-700', 'bg-indigo-50/50');
  };
})();
