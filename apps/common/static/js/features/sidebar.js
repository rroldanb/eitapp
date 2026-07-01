(function () {
  function toggleSidebar() {
    const sidebar = document.getElementById('projectSidebar');
    if (!sidebar) return;
    sidebar.classList.toggle('collapsed');
    sidebar.classList.toggle('expanded');
    localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
  }

  document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('projectSidebar');
    if (!sidebar) return;
    if (localStorage.getItem('sidebarCollapsed') === 'true') {
      sidebar.classList.remove('expanded');
      sidebar.classList.add('collapsed');
    }
    sidebar.querySelectorAll('.nav-link').forEach(function (link) {
      const textEl = link.querySelector('.nav-link-text');
      if (textEl && !link.getAttribute('data-tooltip')) {
        link.setAttribute('data-tooltip', textEl.textContent.trim());
      }
    });
  });

  window.toggleSidebar = toggleSidebar;
})();
