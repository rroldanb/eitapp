(function () {
  const dropZone = document.getElementById('drop-zone');
  if (!dropZone) return;

  const fileInput = document.getElementById('file-input');
  const pasteInput = document.getElementById('paste-input');
  const previewContainer = document.getElementById('image-preview-container');
  const previewImg = document.getElementById('image-preview');
  const removePreviewBtn = document.getElementById('remove-preview-btn');
  const form = document.getElementById('project-form');
  const deleteImageInput = document.getElementById('delete-image-input');

  dropZone.addEventListener('dragover', function (e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.add('border-cyan-500', 'bg-cyan-50');
  });
  dropZone.addEventListener('dragleave', function (e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.remove('border-cyan-500', 'bg-cyan-50');
  });
  dropZone.addEventListener('drop', function (e) {
    e.preventDefault();
    e.stopPropagation();
    this.classList.remove('border-cyan-500', 'bg-cyan-50');
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type.startsWith('image/')) handleFile(files[0]);
  });

  if (fileInput) {
    fileInput.addEventListener('change', function () {
      if (this.files.length > 0) handleFile(this.files[0]);
    });
  }

  document.addEventListener('paste', function (e) {
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

  function handleFile(file) {
    if (!file.type.startsWith('image/')) return;
    showPreview(file);
    const dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;
    pasteInput.value = '';
    if (deleteImageInput) deleteImageInput.value = '';
  }

  function handlePaste(blob) {
    const reader = new FileReader();
    reader.onload = function (e) {
      const base64 = e.target.result;
      showPreviewFromUrl(base64);
      pasteInput.value = base64;
      fileInput.value = '';
      if (deleteImageInput) deleteImageInput.value = '';
    };
    reader.readAsDataURL(blob);
  }

  function showPreview(file) {
    const reader = new FileReader();
    reader.onload = function (e) {
      previewImg.src = e.target.result;
      previewContainer.classList.remove('hidden');
    };
    reader.readAsDataURL(file);
  }

  function showPreviewFromUrl(url) {
    previewImg.src = url;
    previewContainer.classList.remove('hidden');
  }

  if (removePreviewBtn) {
    removePreviewBtn.addEventListener('click', function () {
      previewContainer.classList.add('hidden');
      previewImg.src = '';
      fileInput.value = '';
      pasteInput.value = '';
      if (deleteImageInput) deleteImageInput.value = '1';
    });
  }

  if (form) {
    form.addEventListener('submit', function () {
      if (
        deleteImageInput &&
        deleteImageInput.value === '1' &&
        !fileInput.files.length &&
        !pasteInput.value
      ) {
        document.getElementById('image-triggered').value = 'delete';
      }
    });
  }
})();
