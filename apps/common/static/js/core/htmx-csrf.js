/**
 * Inyecta automáticamente el token CSRF de Django en cada request HTMX.
 * Toma el token del input [name="csrfmiddlewaretoken"] en el DOM.
 */
(function() {
  document.body.addEventListener('htmx:configRequest', function(evt) {
    var tokenInput = document.querySelector('[name="csrfmiddlewaretoken"]');
    if (tokenInput) {
      evt.detail.headers['X-CSRFToken'] = tokenInput.value;
    }
  });
})();
