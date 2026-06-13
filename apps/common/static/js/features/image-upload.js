(function() {
  var dropZone = document.getElementById('drop-zone');
  if (!dropZone) return;

  var fileInput = document.getElementById('file-input');
  var pasteInput = document.getElementById('paste-input');
  var previewContainer = document.getElementById('image-preview-container');
  var previewImg = document.getElementById('image-preview');
  var removePreviewBtn = document.getElementById('remove-preview-btn');
  var form = document.getElementById('project-form');
  var deleteImageInput = document.getElementById('delete-image-input');

  dropZone.addEventListener('dragover', function(e) {
    e.preventDefault(); e.stopPropagation();
    this.classList.add('border-cyan-500', 'bg-cyan-50');
  });
  dropZone.addEventListener('dragleave', function(e) {
    e.preventDefault(); e.stopPropagation();
    this.classList.remove('border-cyan-500', 'bg-cyan-50');
  });
  dropZone.addEventListener('drop', function(e) {
    e.preventDefault(); e.stopPropagation();
    this.classList.remove('border-cyan-500', 'bg-cyan-50');
    var files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type.startsWith('image/')) handleFile(files[0]);
  });

  if (fileInput) {
    fileInput.addEventListener('change', function() {
      if (this.files.length > 0) handleFile(this.files[0]);
    });
  }

  document.addEventListener('paste', function(e) {
    var items = e.clipboardData.items;
    for (var i = 0; i < items.length; i++) {
      if (items[i].type.startsWith('image/')) {
        e.preventDefault();
        var blob = items[i].getAsFile();
        if (blob) handlePaste(blob);
        break;
      }
    }
  });

  function handleFile(file) {
    if (!file.type.startsWith('image/')) return;
    showPreview(file);
    var dt = new DataTransfer();
    dt.items.add(file);
    fileInput.files = dt.files;
    pasteInput.value = '';
    if (deleteImageInput) deleteImageInput.value = '';
  }

  function handlePaste(blob) {
    var reader = new FileReader();
    reader.onload = function(e) {
      var base64 = e.target.result;
      showPreviewFromUrl(base64);
      pasteInput.value = base64;
      fileInput.value = '';
      if (deleteImageInput) deleteImageInput.value = '';
    };
    reader.readAsDataURL(blob);
  }

  function showPreview(file) {
    var reader = new FileReader();
    reader.onload = function(e) { previewImg.src = e.target.result; previewContainer.classList.remove('hidden'); };
    reader.readAsDataURL(file);
  }

  function showPreviewFromUrl(url) {
    previewImg.src = url;
    previewContainer.classList.remove('hidden');
  }

  if (removePreviewBtn) {
    removePreviewBtn.addEventListener('click', function() {
      previewContainer.classList.add('hidden');
      previewImg.src = '';
      fileInput.value = '';
      pasteInput.value = '';
      if (deleteImageInput) deleteImageInput.value = '1';
    });
  }

  if (form) {
    form.addEventListener('submit', function() {
      if (deleteImageInput && deleteImageInput.value === '1' && !fileInput.files.length && !pasteInput.value) {
        document.getElementById('image-triggered').value = 'delete';
      }
    });
  }
})();
