(function () {
  const PLACEHOLDER = '00000000-0000-0000-0000-000000000000';
  const configEl = document.getElementById('nodo-file-config');
  function getUrl(field, action) {
    if (!configEl) return '';
    return (
      configEl.dataset[action + field.charAt(0).toUpperCase() + field.slice(1)] || ''
    ).replace(PLACEHOLDER, selectedNodoId || '');
  }

  let selectedNodoId = null;
  let activeField = 'imagen';
  let hasNewImage = false;
  const fieldUrls = {};

  const modal = document.getElementById('nodo-file-modal');
  const dropZone = document.getElementById('nodo-file-drop-zone');
  const uploadBtn = document.getElementById('nodo-file-upload-btn');
  const deleteBtn = document.getElementById('nodo-file-delete-btn');
  const uploadLabel = document.getElementById('nodo-file-upload-label');
  const deleteLabel = document.getElementById('nodo-file-delete-label');

  function el(id) {
    return document.getElementById(id);
  }
  function fieldEl(suffix) {
    return el(activeField + '-' + suffix);
  }

  function getCSRF() {
    const input = document.querySelector('#nodo-file-modal [name=csrfmiddlewaretoken]');
    return input ? input.value : '';
  }

  function showTab(field) {
    document.querySelectorAll('.nodo-file-content').forEach(function (c) {
      c.classList.add('hidden');
    });
    document.querySelectorAll('.nodo-file-tab').forEach(function (t) {
      t.classList.remove('text-indigo-600', 'border-indigo-600');
      t.classList.add('text-gray-500', 'border-transparent');
    });
    el('nodo-file-content-' + field).classList.remove('hidden');
    const tabBtn = document.querySelector('.nodo-file-tab[data-field="' + field + '"]');
    if (tabBtn) {
      tabBtn.classList.remove('text-gray-500', 'border-transparent');
      tabBtn.classList.add('text-indigo-600', 'border-indigo-600');
    }
  }

  function resetField(field) {
    el(field + '-file-input').value = '';
    el(field + '-file-data').value = '';
    el(field + '-preview-container').classList.add('hidden');
    el(field + '-preview').src = '';
  }

  function syncUI() {
    const previewContainer = fieldEl('preview-container');
    const previewImg = fieldEl('preview');
    if (fieldUrls[activeField] && fieldUrls[activeField].currentUrl) {
      previewImg.src = fieldUrls[activeField].currentUrl;
      previewContainer.classList.remove('hidden');
      deleteBtn.classList.remove('hidden');
      deleteLabel.textContent = activeField === 'imagen' ? 'Eliminar imagen' : 'Eliminar plano';
    } else {
      previewContainer.classList.add('hidden');
      previewImg.src = '';
      deleteBtn.classList.add('hidden');
    }
    hasNewImage = false;
    uploadBtn.disabled = true;
    uploadBtn.classList.add('opacity-50', 'cursor-not-allowed');
    uploadLabel.textContent = activeField === 'imagen' ? 'Subir imagen' : 'Subir plano';
    fieldEl('file-input').value = '';
    fieldEl('file-data').value = '';
  }

  function enableUpload(enable) {
    hasNewImage = enable;
    if (enable) {
      uploadBtn.disabled = false;
      uploadBtn.classList.remove('opacity-50', 'cursor-not-allowed');
    } else {
      uploadBtn.disabled = true;
      uploadBtn.classList.add('opacity-50', 'cursor-not-allowed');
    }
  }

  window.switchFileTab = function (field) {
    activeField = field;
    el('nodo-file-active-field').value = field;
    showTab(field);
    syncUI();
  };

  window.openNodoFileModal = function (nodoId, field, imagenUrl, planoUrl) {
    selectedNodoId = nodoId;
    activeField = field;
    el('nodo-file-nodo-id').value = nodoId;
    el('nodo-file-active-field').value = field;
    if (!fieldUrls.imagen) fieldUrls.imagen = {};
    if (!fieldUrls.plano) fieldUrls.plano = {};
    fieldUrls.imagen.currentUrl = imagenUrl || null;
    fieldUrls.plano.currentUrl = planoUrl || null;
    resetField('imagen');
    resetField('plano');
    showTab(field);
    syncUI();
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
  };

  window.closeNodoFileModal = function () {
    modal.classList.add('hidden');
    document.body.style.overflow = '';
    selectedNodoId = null;
  };

  if (dropZone) {
    dropZone.addEventListener('click', function () {
      fieldEl('file-input').click();
    });
    dropZone.addEventListener('keydown', function (e) {
      if (e.key === 'Enter' || e.key === ' ') fieldEl('file-input').click();
    });
    dropZone.addEventListener('dragover', function (e) {
      e.preventDefault();
      e.stopPropagation();
      this.classList.add('border-indigo-500', 'bg-indigo-50');
    });
    dropZone.addEventListener('dragleave', function (e) {
      e.preventDefault();
      e.stopPropagation();
      this.classList.remove('border-indigo-500', 'bg-indigo-50');
    });
    dropZone.addEventListener('drop', function (e) {
      e.preventDefault();
      e.stopPropagation();
      this.classList.remove('border-indigo-500', 'bg-indigo-50');
      const files = e.dataTransfer.files;
      if (files.length > 0 && files[0].type.startsWith('image/')) handleFile(files[0]);
    });
  }

  document.addEventListener('change', function (e) {
    if (e.target.matches('.nodo-file-content input[type="file"]')) {
      if (e.target.files.length > 0) handleFile(e.target.files[0]);
    }
  });

  document.addEventListener('paste', function (e) {
    if (modal.classList.contains('hidden')) return;
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
      if (items[i].type.startsWith('image/')) {
        e.preventDefault();
        const blob = items[i].getAsFile();
        if (blob) handlePaste(blob);
        break;
      }
    }
  });

  document.addEventListener('click', function (e) {
    if (e.target.closest('.nodo-file-remove-preview')) {
      const field = e.target.closest('.nodo-file-remove-preview').getAttribute('data-field');
      el(field + '-preview-container').classList.add('hidden');
      el(field + '-preview').src = '';
      el(field + '-file-input').value = '';
      el(field + '-file-data').value = '';
      if (field === activeField) enableUpload(false);
    }
  });

  function handleFile(file) {
    if (!file.type.startsWith('image/')) return;
    showPreview(file);
    const dt = new DataTransfer();
    dt.items.add(file);
    fieldEl('file-input').files = dt.files;
    fieldEl('file-data').value = '';
    enableUpload(true);
  }

  function handlePaste(blob) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const base64 = e.target.result;
      showPreviewFromUrl(base64);
      fieldEl('file-data').value = base64;
      fieldEl('file-input').value = '';
      enableUpload(true);
    };
    reader.readAsDataURL(blob);
  }

  function showPreview(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      fieldEl('preview').src = e.target.result;
      fieldEl('preview-container').classList.remove('hidden');
      deleteBtn.classList.add('hidden');
    };
    reader.readAsDataURL(file);
  }

  function showPreviewFromUrl(url) {
    fieldEl('preview').src = url;
    fieldEl('preview-container').classList.remove('hidden');
    deleteBtn.classList.add('hidden');
  }

  function buildFormData() {
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', getCSRF());
    const fi = fieldEl('file-input');
    const b64 = fieldEl('file-data');
    if (fi.files.length > 0) fd.append('image', fi.files[0]);
    else if (b64.value) fd.append('image_file', b64.value);
    return fd;
  }

  window.uploadNodoFile = async function () {
    if (!selectedNodoId || !hasNewImage) return;
    const fd = buildFormData();
    if (!fd.has('image') && !fd.has('image_file')) return;
    uploadBtn.disabled = true;
    uploadLabel.textContent = 'Subiendo...';
    try {
      const resp = await fetch(getUrl(activeField, 'upload'), { method: 'POST', body: fd });
      if (resp.ok) {
        const html = await resp.text();
        const row = document.getElementById('nodo-row-' + selectedNodoId);
        if (row) row.outerHTML = html;
        closeNodoFileModal();
      } else {
        let msg = 'Error al subir';
        try {
          const j = await resp.json();
          msg = j.error || msg;
        } catch (_) {}
        showToast(msg, false);
      }
    } catch (e) {
      showToast('Error de red', false);
    } finally {
      uploadLabel.textContent = 'Subir';
      enableUpload(false);
    }
  };

  window.deleteNodoFile = async function () {
    if (!selectedNodoId) return;
    if (
      !confirm('Eliminar ' + (activeField === 'imagen' ? 'la imagen' : 'el plano') + ' del nodo?')
    )
      return;
    const fd = new FormData();
    fd.append('csrfmiddlewaretoken', getCSRF());
    deleteBtn.disabled = true;
    deleteLabel.textContent = 'Eliminando...';
    try {
      const resp = await fetch(getUrl(activeField, 'delete'), { method: 'POST', body: fd });
      if (resp.ok) {
        const html = await resp.text();
        const row = document.getElementById('nodo-row-' + selectedNodoId);
        if (row) row.outerHTML = html;
        closeNodoFileModal();
      } else {
        let msg = 'Error al eliminar';
        try {
          const j = await resp.json();
          msg = j.error || msg;
        } catch (_) {}
        showToast(msg, false);
      }
    } catch (e) {
      showToast('Error de red', false);
    } finally {
      deleteBtn.disabled = false;
      deleteLabel.textContent = 'Eliminar';
    }
  };

  if (uploadBtn) uploadBtn.addEventListener('click', uploadNodoFile);
  if (deleteBtn) deleteBtn.addEventListener('click', deleteNodoFile);

  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') closeNodoFileModal();
  });
  if (modal) {
    modal.addEventListener('click', function (e) {
      if (e.target === this) closeNodoFileModal();
    });
  }
})();
