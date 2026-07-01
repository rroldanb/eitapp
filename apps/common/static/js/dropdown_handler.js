/**
 * Maneja dropdowns del navbar con Tailwind.
 * Patrón: data-dropdown="{id}" en el toggle, [id$="-menu"] como target.
 * Cierra cualquier otro menú abierto al abrir uno nuevo.
 * Cierra todos al hacer clic fuera de .relative.
 */
document.addEventListener('DOMContentLoaded', function () {
  const dropdownToggles = document.querySelectorAll('.dropdown-toggle');

  dropdownToggles.forEach(function (toggle) {
    const dropdownId = toggle.getAttribute('data-dropdown');
    const menu = document.getElementById(dropdownId);

    if (!menu) return;

    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      const isHidden = menu.classList.contains('hidden');

      /* Cerrar otros dropdowns antes de abrir el actual */
      document.querySelectorAll('[id$="-menu"]').forEach(function (otherMenu) {
        if (otherMenu.id !== dropdownId) {
          otherMenu.classList.add('hidden');
          const btn = document.querySelector('[data-dropdown="' + otherMenu.id + '"]');
          if (btn) btn.setAttribute('aria-expanded', 'false');
        }
      });

      /* Toggle */
      if (isHidden) {
        menu.classList.remove('hidden');
        toggle.setAttribute('aria-expanded', 'true');
      } else {
        menu.classList.add('hidden');
        toggle.setAttribute('aria-expanded', 'false');
      }
    });
  });

  /* Cerrar dropdowns al clickear fuera del contenedor .relative */
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.relative')) {
      document.querySelectorAll('[id$="-menu"]').forEach(function (menu) {
        menu.classList.add('hidden');
        const btn = document.querySelector('[data-dropdown="' + menu.id + '"]');
        if (btn) btn.setAttribute('aria-expanded', 'false');
      });
    }
  });
});
