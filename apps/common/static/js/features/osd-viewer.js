(function() {
  var viewerEl = document.getElementById('seadragon-viewer-proyecto');
  if (!viewerEl) return;
  var configEl = document.getElementById('osd-config');
  if (!configEl) return;
  var imagenUrl = configEl.dataset.imageUrl || '';
  if (!imagenUrl) {
    viewerEl.innerHTML = '<div style="color: red; text-align: center; padding: 50px;">No se encontr\u00f3 ninguna imagen para este proyecto</div>';
    return;
  }
  var viewer = OpenSeadragon({
    id: 'seadragon-viewer-proyecto',
    prefixUrl: 'https://cdnjs.cloudflare.com/ajax/libs/openseadragon/2.4.2/images/',
    tileSources: { type: 'image', url: imagenUrl, crossOriginPolicy: 'Anonymous' },
    showZoomControl: false,
    showPanControl: false,
    showFullPageControl: true,
    showHomeControl: false,
    navigationControlAnchor: OpenSeadragon.ControlAnchor.TOP_RIGHT,
    zoomPerClick: 2.0,
    zoomPerScroll: 1.2,
    minZoomLevel: 0.5,
    maxZoomLevel: 10,
    defaultZoomLevel: 1,
    gestureSettingsMouse: {
      clickToZoom: false, dblClickToZoom: true, pinchToZoom: true,
      flickEnabled: true, flickMinSpeed: 120, flickMomentum: 0.25
    },
    navigatorPosition: 'BOTTOM_RIGHT',
    showNavigator: true,
    navigatorSizeRatio: 0.1
  });
  viewer.addHandler('open-failed', function() {
    console.error('Error al cargar la imagen:', imagenUrl);
  });
})();
