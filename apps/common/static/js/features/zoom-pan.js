(function () {
  const zoomState = {};

  function setLocked(imgId, locked) {
    const s = zoomState[imgId];
    if (!s) return;
    s.locked = locked;
    const vp = document.querySelector('[data-viewport="' + imgId + '"]');
    if (!vp) return;
    if (locked) {
      vp.classList.remove('bg-gray-50');
      vp.classList.add('bg-green-50');
      vp.style.cursor = 'default';
    } else {
      vp.classList.remove('bg-green-50');
      vp.classList.add('bg-gray-50');
      vp.style.cursor = 'grab';
    }
  }

  function initZoom(imgId) {
    const img = document.getElementById(imgId);
    const vp = document.querySelector('[data-viewport="' + imgId + '"]');
    if (!img || !vp) return;

    zoomState[imgId] = {
      scale: 1,
      tx: 0,
      ty: 0,
      dragging: false,
      dragStartX: 0,
      dragStartY: 0,
      startTx: 0,
      startTy: 0,
      locked: false,
      clickStartX: 0,
      clickStartY: 0,
    };

    function apply() {
      const s = zoomState[imgId];
      img.style.transform = 'translate(' + s.tx + 'px, ' + s.ty + 'px) scale(' + s.scale + ')';
    }

    function resetZoom() {
      const s = zoomState[imgId];
      s.scale = 1;
      s.tx = 0;
      s.ty = 0;
      s.dragging = false;
      apply();
    }

    function zoomAt(wheelDelta, cx, cy) {
      const s = zoomState[imgId];
      const factor = wheelDelta > 0 ? 1.05 : 1 / 1.05;
      const newScale = Math.max(0.25, Math.min(10, s.scale * factor));
      if (newScale === s.scale) return;
      const ratio = newScale / s.scale;
      s.tx = cx - ratio * (cx - s.tx);
      s.ty = cy - ratio * (cy - s.ty);
      s.scale = newScale;
      apply();
    }

    vp.addEventListener(
      'wheel',
      function (e) {
        if (img.classList.contains('hidden')) return;
        if (zoomState[imgId].locked) return;
        e.preventDefault();
        const rect = vp.getBoundingClientRect();
        zoomAt(e.deltaY < 0 ? 1 : -1, rect.width / 2, rect.height / 2);
      },
      { passive: false },
    );

    vp.addEventListener('mousedown', function (e) {
      if (img.classList.contains('hidden')) return;
      if (e.button !== 0) return;
      const s = zoomState[imgId];
      s.clickStartX = e.clientX;
      s.clickStartY = e.clientY;
      if (s.locked) return;
      vp.focus();
      s.dragging = true;
      s.dragStartX = e.clientX;
      s.dragStartY = e.clientY;
      s.startTx = s.tx;
      s.startTy = s.ty;
      vp.style.cursor = 'grabbing';
    });

    document.addEventListener('mousemove', function (e) {
      const s = zoomState[imgId];
      if (!s.dragging) return;
      e.preventDefault();
      s.tx = s.startTx + (e.clientX - s.dragStartX);
      s.ty = s.startTy + (e.clientY - s.dragStartY);
      apply();
    });

    document.addEventListener('mouseup', function () {
      const s = zoomState[imgId];
      if (s.dragging) {
        s.dragging = false;
        vp.style.cursor = s.locked ? 'default' : 'grab';
      }
    });

    vp.addEventListener('dblclick', function () {
      if (img.classList.contains('hidden')) return;
      if (zoomState[imgId].locked) return;
      resetZoom();
    });

    vp.addEventListener('click', function (e) {
      if (img.classList.contains('hidden')) return;
      const s = zoomState[imgId];
      const moved =
        Math.abs(e.clientX - s.clickStartX) > 5 || Math.abs(e.clientY - s.clickStartY) > 5;
      if (moved) return;
      setLocked(imgId, !s.locked);
    });

    return { reset: resetZoom, zoomAt: zoomAt };
  }

  function resetZoomFor(imgId) {
    if (zoomState[imgId]) {
      zoomState[imgId].scale = 1;
      zoomState[imgId].tx = 0;
      zoomState[imgId].ty = 0;
      const img = document.getElementById(imgId);
      if (img) img.style.transform = '';
      setLocked(imgId, false);
    }
  }

  function showNodoPreview(nodoId, imagesUrlTpl) {
    const preview = document.getElementById('nodo-images-preview');
    if (!nodoId) {
      preview.classList.add('hidden');
      return;
    }
    const url = imagesUrlTpl.replace('00000000-0000-0000-0000-000000000000', nodoId);
    fetch(url)
      .then(function (r) {
        return r.json();
      })
      .then(function (data) {
        const img = document.getElementById('preview-imagen');
        const pln = document.getElementById('preview-plano');
        const imgEmpty = document.getElementById('preview-imagen-empty');
        const plnEmpty = document.getElementById('preview-plano-empty');
        document.getElementById('preview-plano-label').textContent = data.nombre || '';
        resetZoomFor('preview-imagen');
        resetZoomFor('preview-plano');
        if (data.imagen) {
          img.src = data.imagen;
          img.classList.remove('hidden');
          imgEmpty.classList.add('hidden');
        } else {
          img.classList.add('hidden');
          img.src = '';
          imgEmpty.classList.remove('hidden');
        }
        if (data.plano) {
          pln.src = data.plano;
          pln.classList.remove('hidden');
          plnEmpty.classList.add('hidden');
        } else {
          pln.classList.add('hidden');
          pln.src = '';
          plnEmpty.classList.remove('hidden');
        }
        if (data.plano || data.imagen) preview.classList.remove('hidden');
        else preview.classList.add('hidden');
      })
      .catch(function () {
        preview.classList.add('hidden');
      });
  }

  document.addEventListener('change', function (e) {
    if (e.target.matches('select[name="nodo"]')) {
      const tpl = document.getElementById('puntos-control-list-config');
      showNodoPreview(e.target.value, tpl ? tpl.dataset.imagesUrlTpl : '');
    }
  });

  document.addEventListener('click', function (e) {
    const btn = e.target.closest('.zoom-btn');
    if (!btn) return;
    const targetId = btn.getAttribute('data-target');
    const action = btn.getAttribute('data-action');
    if (!targetId || !zoomState[targetId]) return;
    const s = zoomState[targetId];
    if (action !== 'reset' && s.locked) return;
    const vp = document.querySelector('[data-viewport="' + targetId + '"]');
    if (!vp) return;
    if (action === 'zoom-in') {
      const zoomRect = vp.getBoundingClientRect();
      const zoomCx = zoomRect.width / 2,
        zoomCy = zoomRect.height / 2;
      const zoomNewScale = Math.min(10, s.scale * 1.3);
      s.tx = zoomCx - (zoomNewScale / s.scale) * (zoomCx - s.tx);
      s.ty = zoomCy - (zoomNewScale / s.scale) * (zoomCy - s.ty);
      s.scale = zoomNewScale;
    } else if (action === 'zoom-out') {
      const zoomRect = vp.getBoundingClientRect();
      const zoomCx = zoomRect.width / 2,
        zoomCy = zoomRect.height / 2;
      const zoomNewScale = Math.max(0.25, s.scale / 1.3);
      s.tx = zoomCx - (zoomNewScale / s.scale) * (zoomCx - s.tx);
      s.ty = zoomCy - (zoomNewScale / s.scale) * (zoomCy - s.ty);
      s.scale = zoomNewScale;
    } else if (action === 'reset') {
      s.scale = 1;
      s.tx = 0;
      s.ty = 0;
    }
    const img = document.getElementById(targetId);
    if (img)
      img.style.transform = 'translate(' + s.tx + 'px, ' + s.ty + 'px) scale(' + s.scale + ')';
  });

  initZoom('preview-imagen');
  initZoom('preview-plano');
})();
