/**
 * CRUD Events - Manejador genérico de eventos HTMX para todas las tablas
 * Gestiona: toasts, animaciones, actualizaciones de contador, eventos CRUD
 */

// ========== CONFIG ==========

/**
 * Obtiene config desde el elemento data-crud-config
 * Esperado: data-crud-config data-table-id="..." data-model-name="..." data-csrf-token="..."
 */
function getConfig() {
  const configEl = document.querySelector('[data-crud-config]');
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

const config = getConfig();

// ========== TOAST NOTIFICATIONS ==========

/**
 * Muestra una notificación toast
 * @param {string} message - Mensaje a mostrar
 * @param {boolean} isSuccess - true para éxito, false para error
 * @param {number} duration - Duración en ms (default 3000)
 */
function showToast(message, isSuccess = true, duration = 3000) {
  const toast = document.createElement('div');
  const className = isSuccess ? 'toast-success' : 'toast-error';
  toast.className = `toast-notification ${className}`;
  toast.textContent = message;
  toast.setAttribute('role', 'status');
  toast.setAttribute('aria-live', 'polite');

  document.body.appendChild(toast);
  requestAnimationFrame(() => {
    toast.classList.add('show');
  });

  // Auto-remove después de duration
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, duration);
}

// ========== CONTADOR ==========

/**
 * Actualiza el badge contador de items
 * @param {string} operation - 'add' o 'remove'
 * @param {number} value - Valor a sumar/restar (default 1)
 */
function updateItemCount(operation = 'add', value = 1) {
  const badge = document.getElementById('items-count-badge');
  const new_num = document.getElementById('new_number');
  if (!badge) return;

  let count = parseInt(badge.textContent) || 0;
  if (operation === 'add') {
    count += value;
  } else if (operation === 'remove') {
    count -= value;
  }
  if (new_num) { new_num.value = count+1};
  badge.textContent = count;
}




// ========== BULK UPDATE ==========

/**
 * Obtiene todos los items editados de la tabla
 * @returns {Array} Lista de {id, campo1, campo2, ...}
 */
function getEditedItems() {
  const table = document.getElementById(config.tableId);
  if (!table) return [];

  const items = [];
  const rows = table.querySelectorAll('tbody tr[data-item-id]');

  rows.forEach(row => {
    const itemId = row.dataset.itemId;
    if (!itemId) return;

    const item = { id: itemId };
    const inputs = row.querySelectorAll('input[name]');

    inputs.forEach(input => {
      item[input.name] = input.value;
    });

    items.push(item);
  });

  return items;
}

/**
 * Maneja el guardado en lote de todos los items
 */
function handleBulkSave() {
  const items = getEditedItems();
  if (items.length === 0) {
    showToast('No hay cambios para guardar', false);
    return;
  }

  // Validar que no haya inputs vacíos
  const hasEmpty = items.some(item =>
    Object.values(item).some(val => val === '' || val === null)
  );

  if (hasEmpty) {
    showToast('Por favor completa todos los campos', false);
    return;
  }

  // Enviar bulk update
  fetch(`?bulk-update`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': config.csrfToken,
    },
    body: JSON.stringify(items),
  })
    .then(resp => resp.json())
    .then(data => {
      if (data.success) {
        showToast(`${data.updated_count} ${config.modelName} actualizados`, true);
        location.reload();
      } else {
        showToast(data.error || 'Error en actualización en lote', false);
      }
    })
    .catch(err => {
      showToast(`Error: ${err.message}`, false);
    });
}

// ========== HTMX EVENT HANDLERS ==========

document.addEventListener('DOMContentLoaded', () => {
  // Manejador antes del swap HTMX: evita duplicados en errores de validación


document.addEventListener('htmx:beforeSwap', (event) => {
    if (event.detail.xhr?.status === 400) {
        const ct = event.detail.xhr.getResponseHeader('Content-Type') || '';
        if (ct.includes('text/html')) {
            event.detail.swapBehavior = 'outerHTML';
            const msg = event.detail.xhr.getResponseHeader('X-Form-Error')
                        || 'Corrige los errores en el formulario';
            showToast(msg, false, 5000);
        }
    }
});

// document.addEventListener('htmx:beforeSwap', (event) => {
//   if (event.detail.xhr?.status === 400) {
//     const ct = event.detail.xhr.getResponseHeader('Content-Type') || '';
//     if (ct.includes('text/html')) {
//       event.detail.swapBehavior = 'outerHTML';
//       showToast('Corrige los errores en el formulario', false);
//     }
//   }
// });

  // document.addEventListener('htmx:beforeSwap', (event) => {
  //   if (event.detail.xhr?.status === 400) {
  //     const ct = event.detail.xhr.getResponseHeader('Content-Type') || '';
  //     if (ct.includes('text/html')) {
  //       event.detail.swapBehavior = 'outerHTML';
  //     }
  //   }
  // });

  // Manejador antes de cualquier request HTMX
  document.addEventListener('htmx:beforeRequest', (event) => {
    const method = event.detail.xhr?.method;
    const trigger = event.detail.elt || event.detail.target;

    // Agregar clase de fade-out para deletes
    if (method === 'DELETE') {
      const row = trigger?.closest('tr');
      if (row) {
        row.classList.add('row-fade-out');
      }
    }
  });

  // Manejador después de cualquier request HTMX
  document.addEventListener('htmx:afterRequest', (event) => {
    const status = event.detail.xhr?.status;
    const successful = event.detail.successful;
    const trigger = event.detail.elt || event.detail.target;
    const action = trigger?.dataset?.action;
    const row = trigger?.closest('tr') || event.detail.target?.closest('tr');

    // Éxito (200, 201, 204)
    if ([200, 201, 204].includes(status)) {
      if (action === 'create') {
        // Restaurar UI del form si estaba en estado de error
        const formRow = document.querySelector('tr[id^="new-"][id$="-form-row"]');
        if (formRow) {
          const td = formRow.querySelector('td');
          if (td) {
            td.classList.remove('bg-red-50', 'bg-red-100');
            td.classList.add('bg-green-100');
          }
          formRow.querySelectorAll('.error-message, .field-error').forEach(el => el.remove());
        }
        showToast(`${config.modelName}: Creado exitosamente`, true);
        setTimeout(() => updateItemCount('add'), 400);

      } else if (action === 'update') {
        showToast(`${config.modelName}: Actualizado exitosamente`, true);
      } else if (action === 'delete') {
        updateItemCount('remove');
        showToast(`${config.modelName}: Eliminado exitosamente`, true);
        // Remover fila después de que la animación termine
        setTimeout(() => {
          if (row) row.remove();
        }, 400);
      }
    }
    // Error

else if (status >= 400) {
  const ct = event.detail.xhr?.getResponseHeader('Content-Type') || '';
  let errorMsg = '';
  if (ct.includes('application/json')) {
    try {
      const data = JSON.parse(event.detail.xhr.responseText);
      errorMsg = data.error || data.message || '';
    } catch (e) {}
  }
  if (errorMsg) showToast(errorMsg, false);
}

    // else if (status >= 400) {
    //   const ct = event.detail.xhr?.getResponseHeader('Content-Type') || '';
    //   let errorMsg = '';
    //   if (ct.includes('application/json')) {
    //     try {
    //       const data = JSON.parse(event.detail.xhr.responseText);
    //       errorMsg = data.error || data.message || '';
    //     } catch (e) {}
    //   } else if (ct.includes('text/html')) {
    //     errorMsg = 'Corrige los errores en el formulario';
    //   }
    //   if (!errorMsg) {
    //     const action_text = action ? action.charAt(0).toUpperCase() + action.slice(1) : 'Operación';
    //     errorMsg = `${action_text} fallido (${status})`;
    //   }
    //   showToast(errorMsg, false);
    // }
  });

  // Vincular botones de submit/cancel (si existen)
  const submitBtn = document.querySelector('[data-action="bulk-save"]');
  const cancelBtn = document.querySelector('[data-action="bulk-cancel"]');

  if (submitBtn) {
    submitBtn.addEventListener('click', handleBulkSave);
  }

  if (cancelBtn) {
    cancelBtn.addEventListener('click', () => {
      location.reload();
    });
  }
});
