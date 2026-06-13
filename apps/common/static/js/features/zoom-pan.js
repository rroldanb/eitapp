(function() {
  var zoomState = {};

  function initZoom(imgId) {
    var img = document.getElementById(imgId);
    var vp = document.querySelector('[data-viewport="' + imgId + '"]');
    if (!img || !vp) return;

    zoomState[imgId] = { scale: 1, tx: 0, ty: 0, dragging: false, dragStartX: 0, dragStartY: 0, startTx: 0, startTy: 0 };

    function apply() {
      var s = zoomState[imgId];
      img.style.transform = 'translate(' + s.tx + 'px, ' + s.ty + 'px) scale(' + s.scale + ')';
    }

    function resetZoom() {
      zoomState[imgId] = { scale: 1, tx: 0, ty: 0, dragging: false, dragStartX: 0, dragStartY: 0, startTx: 0, startTy: 0 };
      apply();
    }

    function zoomAt(wheelDelta, cx, cy) {
      var s = zoomState[imgId];
      var factor = wheelDelta > 0 ? 1.05 : 1 / 1.05;
      var newScale = Math.max(0.25, Math.min(10, s.scale * factor));
      if (newScale === s.scale) return;
      var ratio = newScale / s.scale;
      s.tx = cx - ratio * (cx - s.tx);
      s.ty = cy - ratio * (cy - s.ty);
      s.scale = newScale;
      apply();
    }

    vp.addEventListener('wheel', function(e) {
      if (img.classList.contains('hidden')) return;
      e.preventDefault();
      var rect = vp.getBoundingClientRect();
      zoomAt(e.deltaY < 0 ? 1 : -1, rect.width / 2, rect.height / 2);
    }, { passive: false });

    vp.addEventListener('mousedown', function(e) {
      if (img.classList.contains('hidden')) return;
      if (e.button !== 0) return;
      vp.focus();
      var s = zoomState[imgId];
      s.dragging = true;
      s.dragStartX = e.clientX;
      s.dragStartY = e.clientY;
      s.startTx = s.tx;
      s.startTy = s.ty;
      vp.style.cursor = 'grabbing';
    });

    document.addEventListener('mousemove', function(e) {
      var s = zoomState[imgId];
      if (!s.dragging) return;
      e.preventDefault();
      s.tx = s.startTx + (e.clientX - s.dragStartX);
      s.ty = s.startTy + (e.clientY - s.dragStartY);
      apply();
    });

    document.addEventListener('mouseup', function() {
      var s = zoomState[imgId];
      if (s.dragging) {
        s.dragging = false;
        vp.style.cursor = 'grab';
      }
    });

    vp.addEventListener('dblclick', function() {
      if (img.classList.contains('hidden')) return;
      resetZoom();
    });

    return { reset: resetZoom, zoomAt: zoomAt };
  }

  function resetZoomFor(imgId) {
    if (zoomState[imgId]) {
      zoomState[imgId].scale = 1;
      zoomState[imgId].tx = 0;
      zoomState[imgId].ty = 0;
      var img = document.getElementById(imgId);
      if (img) img.style.transform = '';
    }
  }

  function showNodoPreview(nodoId, imagesUrlTpl) {
    var preview = document.getElementById('nodo-images-preview');
    if (!nodoId) { preview.classList.add('hidden'); return; }
    var url = imagesUrlTpl.replace('00000000-0000-0000-0000-000000000000', nodoId);
    fetch(url)
      .then(function(r) { return r.json(); })
      .then(function(data) {
        var img = document.getElementById('preview-imagen');
        var pln = document.getElementById('preview-plano');
        var imgEmpty = document.getElementById('preview-imagen-empty');
        var plnEmpty = document.getElementById('preview-plano-empty');
        document.getElementById('preview-plano-label').textContent = data.nombre || '';
        resetZoomFor('preview-imagen');
        resetZoomFor('preview-plano');
        if (data.imagen) { img.src = data.imagen; img.classList.remove('hidden'); imgEmpty.classList.add('hidden'); }
        else { img.classList.add('hidden'); img.src = ''; imgEmpty.classList.remove('hidden'); }
        if (data.plano) { pln.src = data.plano; pln.classList.remove('hidden'); plnEmpty.classList.add('hidden'); }
        else { pln.classList.add('hidden'); pln.src = ''; plnEmpty.classList.remove('hidden'); }
        if (data.plano || data.imagen) preview.classList.remove('hidden');
        else preview.classList.add('hidden');
      })
      .catch(function() { preview.classList.add('hidden'); });
  }

  document.addEventListener('change', function(e) {
    if (e.target.matches('select[name="nodo"]')) {
      var tpl = document.getElementById('puntos-control-list-config');
      showNodoPreview(e.target.value, tpl ? tpl.dataset.imagesUrlTpl : '');
    }
  });

  document.addEventListener('click', function(e) {
    var btn = e.target.closest('.zoom-btn');
    if (!btn) return;
    var targetId = btn.getAttribute('data-target');
    var action = btn.getAttribute('data-action');
    if (!targetId || !zoomState[targetId]) return;
    var s = zoomState[targetId];
    var vp = document.querySelector('[data-viewport="' + targetId + '"]');
    if (!vp) return;
    if (action === 'zoom-in') {
      var rect = vp.getBoundingClientRect();
      var cx = rect.width / 2, cy = rect.height / 2;
      var newScale = Math.min(10, s.scale * 1.3);
      s.tx = cx - (newScale / s.scale) * (cx - s.tx);
      s.ty = cy - (newScale / s.scale) * (cy - s.ty);
      s.scale = newScale;
    } else if (action === 'zoom-out') {
      var rect = vp.getBoundingClientRect();
      var cx = rect.width / 2, cy = rect.height / 2;
      var newScale = Math.max(0.25, s.scale / 1.3);
      s.tx = cx - (newScale / s.scale) * (cx - s.tx);
      s.ty = cy - (newScale / s.scale) * (cy - s.ty);
      s.scale = newScale;
    } else if (action === 'reset') {
      s.scale = 1; s.tx = 0; s.ty = 0;
    }
    var img = document.getElementById(targetId);
    if (img) img.style.transform = 'translate(' + s.tx + 'px, ' + s.ty + 'px) scale(' + s.scale + ')';
  });

  initZoom('preview-imagen');
  initZoom('preview-plano');
})();
