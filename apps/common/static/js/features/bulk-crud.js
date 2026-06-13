(function() {
  function getConfig() {
    var configEl = document.querySelector('[data-crud-config]');
    if (!configEl) {
      return {
        tableId: 'items-table',
        modelName: 'items',
        csrfToken: document.querySelector('[name="csrfmiddlewaretoken"]')?.value || '',
      };
    }
    return {
      tableId: configEl.dataset.tableId || 'items-table',
      modelName: configEl.dataset.modelName || 'items',
      csrfToken: configEl.dataset.csrfToken || '',
    };
  }

  var config = getConfig();

  function updateItemCount(operation, value) {
    if (value === undefined) value = 1;
    var badge = document.getElementById('items-count-badge');
    var newNum = document.getElementById('new_number');
    if (!badge) return;
    var count = parseInt(badge.textContent) || 0;
    if (operation === 'add') count += value;
    else if (operation === 'remove') count -= value;
    if (newNum) newNum.value = count + 1;
    badge.textContent = count;
  }

  function getEditedItems() {
    var table = document.getElementById(config.tableId);
    if (!table) return [];
    var items = [];
    var rows = table.querySelectorAll('tbody tr[data-item-id]');
    rows.forEach(function(row) {
      var itemId = row.dataset.itemId;
      if (!itemId) return;
      var item = { id: itemId };
      var inputs = row.querySelectorAll('input[name]');
      inputs.forEach(function(input) { item[input.name] = input.value; });
      items.push(item);
    });
    return items;
  }

  function handleBulkSave() {
    var items = getEditedItems();
    if (items.length === 0) { showToast('No hay cambios para guardar', false); return; }
    var hasEmpty = items.some(function(item) {
      return Object.values(item).some(function(val) { return val === '' || val === null; });
    });
    if (hasEmpty) { showToast('Por favor completa todos los campos', false); return; }
    fetch('?bulk-update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json', 'X-CSRFToken': config.csrfToken },
      body: JSON.stringify(items),
    })
      .then(function(resp) { return resp.json(); })
      .then(function(data) {
        if (data.success) { showToast(data.updated_count + ' ' + config.modelName + ' actualizados', true); location.reload(); }
        else { showToast(data.error || 'Error en actualización en lote', false); }
      })
      .catch(function(err) { showToast('Error: ' + err.message, false); });
  }

  document.addEventListener('htmx:beforeSwap', function(event) {
    if (event.detail.xhr && event.detail.xhr.status === 400) {
      var ct = event.detail.xhr.getResponseHeader('Content-Type') || '';
      if (ct.indexOf('text/html') !== -1) {
        event.detail.swapBehavior = 'outerHTML';
        var msg = event.detail.xhr.getResponseHeader('X-Form-Error') || 'Corrige los errores en el formulario';
        showToast(msg, false, 5000);
      }
    }
  });

  document.addEventListener('htmx:beforeRequest', function(event) {
    var method = event.detail.xhr && event.detail.xhr.method;
    var trigger = event.detail.elt || event.detail.target;
    if (method === 'DELETE') {
      var row = trigger && trigger.closest('tr');
      if (row) row.classList.add('row-fade-out');
    }
  });

  document.addEventListener('htmx:afterRequest', function(event) {
    var status = event.detail.xhr && event.detail.xhr.status;
    var successful = event.detail.successful;
    var trigger = event.detail.elt || event.detail.target;
    var action = trigger && trigger.dataset && trigger.dataset.action;
    var row = (trigger && trigger.closest('tr')) || (event.detail.target && event.detail.target.closest('tr'));

    if ([200, 201, 204].indexOf(status) !== -1) {
      if (action === 'create') {
        var formRow = document.querySelector('tr[id^="new-"][id$="-form-row"]');
        if (formRow) {
          var td = formRow.querySelector('td');
          if (td) { td.classList.remove('bg-red-50', 'bg-red-100'); td.classList.add('bg-green-100'); }
          formRow.querySelectorAll('.error-message, .field-error').forEach(function(el) { el.remove(); });
        }
        showToast(config.modelName + ': Creado exitosamente', true);
        setTimeout(function() { updateItemCount('add'); }, 400);
      } else if (action === 'update') {
        showToast(config.modelName + ': Actualizado exitosamente', true);
      } else if (action === 'delete') {
        updateItemCount('remove');
        showToast(config.modelName + ': Eliminado exitosamente', true);
        setTimeout(function() { if (row) row.remove(); }, 400);
      }
    } else if (status >= 400) {
      var ct = event.detail.xhr && event.detail.xhr.getResponseHeader('Content-Type') || '';
      var errorMsg = '';
      if (ct.indexOf('application/json') !== -1) {
        try { var data = JSON.parse(event.detail.xhr.responseText); errorMsg = data.error || data.message || ''; } catch(e) {}
      }
      if (errorMsg) showToast(errorMsg, false);
    }
  });

  document.addEventListener('DOMContentLoaded', function() {
    var submitBtn = document.querySelector('[data-action="bulk-save"]');
    var cancelBtn = document.querySelector('[data-action="bulk-cancel"]');
    if (submitBtn) submitBtn.addEventListener('click', handleBulkSave);
    if (cancelBtn) cancelBtn.addEventListener('click', function() { location.reload(); });
  });

  window.updateItemCount = updateItemCount;
})();
