/**
 * Dropdown Handler - Maneja dropdowns del navbar con Tailwind
 */

document.addEventListener('DOMContentLoaded', function() {
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    
    dropdownToggles.forEach(toggle => {
        const dropdownId = toggle.getAttribute('data-dropdown');
        const menu = document.getElementById(dropdownId);
        
        if (!menu) return;
        
        // Toggle on click
        toggle.addEventListener('click', (e) => {
            e.preventDefault();
            const isHidden = menu.classList.contains('hidden');
            
            // Cerrar otros dropdowns
            document.querySelectorAll('[id$="-menu"]').forEach(otherMenu => {
                if (otherMenu.id !== dropdownId) {
                    otherMenu.classList.add('hidden');
                }
            });
            
            // Toggle actual
            if (isHidden) {
                menu.classList.remove('hidden');
            } else {
                menu.classList.add('hidden');
            }
        });
    });
    
    // Cerrar dropdowns al clickear fuera
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.relative')) {
            document.querySelectorAll('[id$="-menu"]').forEach(menu => {
                menu.classList.add('hidden');
            });
        }
    });
});
