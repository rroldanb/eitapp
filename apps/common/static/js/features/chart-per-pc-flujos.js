(function () {
  'use strict';
  var _chartsData = [];

  function buildDatasets(datasets) {
    return datasets.map(function (ds) {
      return {
        label: ds.label,
        data: ds.data,
        borderColor: ds.borderColor || 'rgba(99, 102, 241, 1)',
        backgroundColor: ds.backgroundColor || 'rgba(99, 102, 241, 0.1)',
        fill: ds.fill !== undefined ? ds.fill : false,
        tension: ds.tension || 0.3,
        pointRadius: ds.pointRadius || 2,
        pointHoverRadius: ds.pointHoverRadius || 4,
        borderWidth: ds.borderWidth || 2,
        spanGaps: ds.spanGaps || false,
      };
    });
  }

  function makeChartOptions(titleText) {
    return {
      responsive: true,
      maintainAspectRatio: false,
      interaction: { mode: 'index', intersect: false },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: 'VEQ/15min' },
          grid: { color: 'rgba(0,0,0,0.05)' },
        },
        x: {
          title: { display: true, text: 'Hora' },
          grid: { display: false },
          ticks: { maxRotation: 45, font: { size: 10 } },
        },
      },
      plugins: {
        legend: { position: 'top', labels: { usePointStyle: true, boxWidth: 12, padding: 14 } },
        tooltip: {
          callbacks: {
            label: function (context) {
              var label = context.dataset.label || '';
              var val = context.parsed.y;
              if (val === null || val === undefined) return label + ': \u2014';
              return label + ': ' + val.toFixed(2) + ' VEQ';
            },
          },
        },
      },
    };
  }

  var bandPlugin = {
    id: 'pcPeakBands',
    beforeDraw: function (chart) {
      var bandas = chart._bandas || [];
      if (bandas.length === 0) return;
      var ctx = chart.ctx;
      var chartArea = chart.chartArea;
      var meta = chart.getDatasetMeta(0);
      if (!meta || !meta.data || meta.data.length === 0) return;

      bandas.forEach(function (band) {
        var fromIdx = Math.max(0, band.from);
        var toIdx = Math.min(meta.data.length - 1, band.to - 1);
        if (fromIdx > toIdx) return;

        var x1 = meta.data[fromIdx].x;
        if (band.from > 0) {
          var prev = meta.data[band.from - 1];
          if (prev) x1 = (prev.x + meta.data[fromIdx].x) / 2;
        }
        var x2 = meta.data[toIdx].x;
        if (band.to < meta.data.length) {
          var next = meta.data[band.to];
          if (next) x2 = (meta.data[toIdx].x + next.x) / 2;
        }

        var isPM = band.label === 'PM-L';
        ctx.save();
        ctx.fillStyle = isPM
          ? 'rgba(59, 130, 246, 0.15)'
          : 'rgba(251, 146, 60, 0.15)';
        ctx.fillRect(x1, chartArea.top, x2 - x1, chartArea.bottom - chartArea.top);

        ctx.fillStyle = isPM
          ? 'rgba(59, 130, 246, 0.7)'
          : 'rgba(251, 146, 60, 0.7)';
        ctx.font = '10px sans-serif';
        ctx.textAlign = 'left';
        ctx.fillText(band.label, x1 + 3, chartArea.top + 11);
        ctx.restore();
      });
    },
  };

  function getChartDef(nodoId) {
    for (var i = 0; i < _chartsData.length; i++) {
      if (_chartsData[i].nodo_id === nodoId) return _chartsData[i];
    }
    return null;
  }

  function renderChart(canvasId, chartDef) {
    var ctx = document.getElementById(canvasId);
    if (!ctx) return;

    var nodoId = chartDef.nodo_id;
    if (window._perPcCharts && window._perPcCharts[nodoId]) {
      window._perPcCharts[nodoId].destroy();
      delete window._perPcCharts[nodoId];
    }

    if (!chartDef.labels || chartDef.labels.length === 0) {
      ctx.parentElement.innerHTML =
        '<p class="text-gray-500 text-center py-6">Sin datos</p>';
      return;
    }

    if (!window._perPcCharts) window._perPcCharts = {};

    var chart = new Chart(ctx, {
      type: 'line',
      data: {
        labels: chartDef.labels,
        datasets: buildDatasets(chartDef.datasets),
      },
      options: makeChartOptions(chartDef.label),
      plugins: [bandPlugin],
    });
    chart._bandas = chartDef.bandas || [];
    window._perPcCharts[nodoId] = chart;
  }

  // ── Toggle movimiento ──
  function toggleMovimiento(nodoId, movimientoId, show) {
    var chart = window._perPcCharts && window._perPcCharts[nodoId];
    if (!chart) return;
    var chartDef = getChartDef(nodoId);
    if (!chartDef) return;

    for (var i = 0; i < chart.data.datasets.length; i++) {
      var ds = chart.data.datasets[i];
      var dsDef = chartDef.datasets[i];
      if (dsDef && dsDef.movimiento_id === movimientoId) {
        var meta = chart.getDatasetMeta(i);
        meta.hidden = !show;
        chart.update();
        break;
      }
    }

    // Update button styling
    var btn = document.querySelector(
      '.movimiento-btn[data-nodo-id="' + nodoId + '"][data-movimiento-id="' + movimientoId + '"]'
    );
    if (btn) {
      btn.setAttribute('data-active', show ? 'true' : 'false');
      var color = btn.style.borderColor;
      if (show) {
        btn.style.background = color + '15';
        btn.style.opacity = '1';
      } else {
        btn.style.background = 'transparent';
        btn.style.opacity = '0.4';
      }
    }
  }

  // ── Modal ──
  function openModal(chartDef) {
    var existing = document.getElementById('pcChartModal');
    if (existing) existing.remove();

    var modal = document.createElement('div');
    modal.id = 'pcChartModal';
    modal.style.cssText =
      'position:fixed;top:0;left:0;width:100%;height:100%;z-index:9999;' +
      'background:rgba(0,0,0,0.6);display:flex;align-items:center;justify-content:center;' +
      'padding:2rem;';

    var card = document.createElement('div');
    card.style.cssText =
      'background:#fff;border-radius:12px;width:100%;max-width:1100px;' +
      'max-height:90vh;overflow:hidden;box-shadow:0 20px 60px rgba(0,0,0,0.3);';

    var header = document.createElement('div');
    header.style.cssText =
      'display:flex;justify-content:space-between;align-items:center;' +
      'padding:0.75rem 1.25rem;border-bottom:1px solid #e5e7eb;';

    var title = document.createElement('h3');
    title.textContent = chartDef.label + ' \u2014 Flujo 15 min (expandido)';
    title.style.cssText = 'margin:0;font-size:1rem;font-weight:600;color:#1f2937;';

    var closeBtn = document.createElement('button');
    closeBtn.innerHTML = '\u2715';
    closeBtn.style.cssText =
      'background:none;border:none;font-size:1.25rem;color:#6b7280;cursor:pointer;' +
      'padding:4px 10px;border-radius:4px;line-height:1;';
    closeBtn.onmouseover = function () { closeBtn.style.background = '#f3f4f6'; };
    closeBtn.onmouseout = function () { closeBtn.style.background = 'none'; };
    closeBtn.onclick = function () { modal.remove(); };

    header.appendChild(title);
    header.appendChild(closeBtn);

    var body = document.createElement('div');
    body.style.cssText = 'padding:1.25rem;position:relative;min-height:400px;';

    var canvas = document.createElement('canvas');
    canvas.id = 'pcChartModal-canvas';
    canvas.width = 1100;
    canvas.height = 380;
    canvas.style.cssText = 'width:100%;display:block;';

    body.appendChild(canvas);
    card.appendChild(header);
    card.appendChild(body);
    modal.appendChild(card);

    modal.addEventListener('click', function (e) {
      if (e.target === modal) modal.remove();
    });
    function _onKey(e) {
      if (e.key === 'Escape') { modal.remove(); document.removeEventListener('keydown', _onKey); }
    }
    document.addEventListener('keydown', _onKey);

    document.body.appendChild(modal);

    var modalChart = new Chart(canvas, {
      type: 'line',
      data: {
        labels: chartDef.labels,
        datasets: buildDatasets(chartDef.datasets),
      },
      options: makeChartOptions(chartDef.label),
      plugins: [bandPlugin],
    });
    modalChart._bandas = chartDef.bandas || [];

    // Apply toggles to modal chart too
    if (chartDef.movimientos) {
      for (var i = 0; i < chartDef.datasets.length; i++) {
        var dsDef = chartDef.datasets[i];
        var mov = null;
        for (var m = 0; m < chartDef.movimientos.length; m++) {
          if (chartDef.movimientos[m].id === dsDef.movimiento_id) {
            mov = chartDef.movimientos[m];
            break;
          }
        }
        if (mov && !mov.visible) {
          var meta = modalChart.getDatasetMeta(i);
          meta.hidden = true;
          modalChart.update();
        }
      }
    }
  }

  // ── Sequential render guard ──
  var _renderTimer = null;

  // ── Public render (sequential, one per frame) ──
  window.renderPcCharts = function () {
    if (_renderTimer) {
      clearTimeout(_renderTimer);
      _renderTimer = null;
    }

    var dataEl = document.getElementById('per-pc-chart-data');
    if (!dataEl) return;
    try {
      _chartsData = JSON.parse(dataEl.textContent || '[]');
    } catch (e) {
      _chartsData = [];
      return;
    }
    if (_chartsData.length === 0) return;

    var idx = 0;
    function renderNext() {
      if (idx >= _chartsData.length) {
        _renderTimer = null;
        return;
      }
      var chartDef = _chartsData[idx];
      idx++;
      renderChart('pcChart-' + chartDef.nodo_id, chartDef);
      _renderTimer = setTimeout(renderNext, 20);
    }
    renderNext();
  };

  // ── Click: expand modal on chart card ──
  document.addEventListener('click', function (e) {
    var expandBtn = e.target.closest('[data-expand-chart]');
    if (!expandBtn) return;
    var card = expandBtn.closest('.chart-card');
    if (!card) return;
    var nodoId = card.getAttribute('data-nodo-id');
    if (!nodoId) return;
    var chartDef = getChartDef(nodoId);
    if (chartDef) openModal(chartDef);
    return;
  });

  // ── Click: toggle movimiento ──
  document.addEventListener('click', function (e) {
    var movBtn = e.target.closest('.movimiento-btn');
    if (!movBtn) return;
    var nodoId = movBtn.getAttribute('data-nodo-id');
    var movimientoId = movBtn.getAttribute('data-movimiento-id');
    var active = movBtn.getAttribute('data-active') === 'true';
    toggleMovimiento(nodoId, movimientoId, !active);

    // Update chartDef state
    var chartDef = getChartDef(nodoId);
    if (chartDef && chartDef.movimientos) {
      for (var i = 0; i < chartDef.movimientos.length; i++) {
        if (chartDef.movimientos[i].id === movimientoId) {
          chartDef.movimientos[i].visible = !active;
          break;
        }
      }
    }
  });

  // Auto-render on initial page load
  if (document.readyState !== 'loading') {
    window.renderPcCharts();
  } else {
    document.addEventListener('DOMContentLoaded', window.renderPcCharts);
  }
})();
