/**
 * Maneja dropdowns del navbar con Tailwind.
 * Patrón: data-dropdown="{id}" en el toggle, [id$="-menu"] como target.
 * Cierra cualquier otro menú abierto al abrir uno nuevo, EXCEPTO los que
 * sean ancestros del menú actual (necesario para submenús anidados,
 * ej. "Base de datos" dentro de "Admin").
 * Cierra todos al hacer clic fuera de .relative.
 * Cierra todos al presionar Escape.
 * En pantallas lg+ los menús también se abren/cierran con hover.
 */
document.addEventListener('DOMContentLoaded', function () {
  const dropdownToggles = document.querySelectorAll('.dropdown-toggle');

  /* Punto de corte para considerar "desktop" (coincide con el prefijo lg: de Tailwind) */
  const DESKTOP_MEDIA_QUERY = '(min-width: 1024px)';
  const isDesktop = () => window.matchMedia(DESKTOP_MEDIA_QUERY).matches;

  /**
   * Abre un menú y marca su toggle como expandido.
   */
  function openMenu(menu, toggle) {
    menu.classList.remove('hidden');
    toggle.setAttribute('aria-expanded', 'true');
  }

  /**
   * Cierra un menú y marca su toggle como colapsado.
   */
  function closeMenu(menu, toggle) {
    menu.classList.add('hidden');
    toggle.setAttribute('aria-expanded', 'false');
  }

  /**
   * Cierra todos los menús excepto el que coincide con excludeId
   * y excepto los que sean ancestros de excludeToggle (submenús padres).
   */
  function closeOthers(excludeId, excludeToggle) {
    document.querySelectorAll('[id$="-menu"]').forEach(function (otherMenu) {
      const isSelf = otherMenu.id === excludeId;
      const isAncestor = excludeToggle && otherMenu.contains(excludeToggle);
      if (!isSelf && !isAncestor) {
        const btn = document.querySelector('[data-dropdown="' + otherMenu.id + '"]');
        if (btn) closeMenu(otherMenu, btn);
      }
    });
  }

  /**
   * Cierra absolutamente todos los menús (usado en click afuera y Escape).
   */
  function closeAll() {
    document.querySelectorAll('[id$="-menu"]').forEach(function (menu) {
      const btn = document.querySelector('[data-dropdown="' + menu.id + '"]');
      if (btn) closeMenu(menu, btn);
    });
  }

  dropdownToggles.forEach(function (toggle) {
    const dropdownId = toggle.getAttribute('data-dropdown');
    const menu = document.getElementById(dropdownId);

    if (!menu) return;

    /* Contenedor .relative más cercano, usado para detectar mouseleave real */
    const container = toggle.closest('.relative');

    toggle.addEventListener('click', function (e) {
      e.preventDefault();
      e.stopPropagation(); // evita que el click burbujee y afecte al toggle del padre

      const isHidden = menu.classList.contains('hidden');

      /* Cerrar otros dropdowns, excepto ancestros del actual */
      closeOthers(dropdownId, toggle);

      /* Toggle */
      if (isHidden) {
        openMenu(menu, toggle);
      } else {
        closeMenu(menu, toggle);
      }
    });

    /* --- Apertura/cierre con hover, solo en desktop (lg+) --- */
    if (container) {
      container.addEventListener('mouseenter', function () {
        if (!isDesktop()) return;
        closeOthers(dropdownId, toggle);
        openMenu(menu, toggle);
      });

      container.addEventListener('mouseleave', function () {
        if (!isDesktop()) return;
        closeMenu(menu, toggle);
      });
    }
  });

  /* Cerrar dropdowns al clickear fuera del contenedor .relative */
  document.addEventListener('click', function (e) {
    if (!e.target.closest('.relative')) {
      closeAll();
    }
  });

  /* Cerrar todos los dropdowns al presionar Escape */
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') {
      closeAll();
    }
  });
});
