const configElement = document.getElementById('calles-list-config');
const CallesListConfig = {
  proyectoId: configElement?.dataset?.proyectoId || null,
  csrfToken: configElement?.dataset?.csrfToken || null,
};

function showToast(message, isSuccess = true) {
  const toast = document.createElement('div');
  toast.className = `toast-notification ${isSuccess ? 'toast-success' : 'toast-error'}`;
  toast.textContent = message;
  document.body.appendChild(toast);
  setTimeout(() => toast.classList.add('show'), 10);
  setTimeout(() => {
    toast.classList.remove('show');
    setTimeout(() => toast.remove(), 300);
  }, 3000);
}

function updateCount(op) {
  const badge = document.getElementById('calles-count');
  const inputNum = document.getElementById('new_number');
  const currentCount = Number(badge?.textContent) || 0;
  const nextCount = op === 'add' ? currentCount + 1 : currentCount - 1;

  if (badge) {
    badge.textContent = nextCount;
  }

  if (inputNum) {
    inputNum.value = nextCount + 1;
  }
}

function getCalleRows() {
  return document.querySelectorAll('.calle-row[data-calle-id]');
}

function handleBulkSave() {
  const submitAll = document.getElementById('submit-all');
  if (!submitAll) return;

  submitAll.addEventListener('click', async function () {
    const rows = getCalleRows();
    const data = [];
    let hasErrors = false;

    rows.forEach(row => {
      const calleId = row.getAttribute('data-calle-id');
      const numeroInput = row.querySelector('input[name="numero"]');
      const nombreInput = row.querySelector('input[name="nombre"]');

      if (numeroInput && nombreInput) {
        const numero = numeroInput.value.trim();
        const nombre = nombreInput.value.trim();

        if (!nombre) {
          hasErrors = true;
          numeroInput.classList.add('border-red-500');
        } else {
          numeroInput.classList.remove('border-red-500');
          data.push({
            id: calleId,
            numero,
            nombre,
          });
        }
      }
    });

    if (hasErrors) {
      showToast('Hay campos vacíos que deben ser completados', false);
      return;
    }

    if (data.length === 0) {
      showToast('No hay cambios para guardar', false);
      return;
    }

    try {
      const response = await fetch(`/red-vial/proyecto/${CallesListConfig.proyectoId}/calles/bulk-update/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': CallesListConfig.csrfToken,
        },
        body: JSON.stringify(data),
      });

      const result = await response.json();

      if (result.success) {
        rows.forEach(row => {
          row.classList.add('bg-green-100');
          setTimeout(() => row.classList.remove('bg-green-100'), 1500);
        });
        showToast(`✅ Guardadas ${result.updated_count} calles`, true);
      } else {
        showToast('Error: ' + result.error, false);
      }
    } catch (error) {
      showToast('Error de conexión: ' + error.message, false);
    }
  });
}

function handleCancelAll() {
  const cancelAll = document.getElementById('cancel-all');
  if (!cancelAll) return;

  cancelAll.addEventListener('click', function () {
    window.location.reload();
  });
}

function handleHtmxEvents() {
  document.body.addEventListener('htmx:beforeRequest', function (evt) {
    const trigger = evt.detail.elt || evt.detail.target;
    if (!trigger) return;
    if (trigger.dataset.action === 'delete') {
      const row = trigger.closest('tr');
      if (row) {
        row.classList.add('row-fade-out');
      }
    }
  });

  document.body.addEventListener('htmx:afterRequest', function (evt) {
    const trigger = evt.detail.elt || evt.detail.target;
    const successful = evt.detail.successful;
    if (!trigger || !successful) return;

    const action = trigger.dataset.action;
    if (action === 'delete') {
      updateCount('remove');
      showToast('Calle eliminada', false);
      const row = trigger.closest('tr');
      if (row) {
        setTimeout(() => {
          if (row.parentNode) row.remove();
        }, 400);
      }
      return;
    }

    if (action === 'update') {
      showToast('Calle actualizada', true);
      return;
    }

    if (action === 'create') {
      showToast('Calle creada', true);
      setTimeout(() => updateCount('add'), 400);
      return;
    }
  });
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', function () {
    handleBulkSave();
    handleCancelAll();
    handleHtmxEvents();
  });
} else {
  handleBulkSave();
  handleCancelAll();
  handleHtmxEvents();
}
