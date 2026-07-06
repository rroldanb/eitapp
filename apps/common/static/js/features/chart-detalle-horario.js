(function () {
  'use strict';

  window.renderDetalleHorario = function () {
    if (window._detalleHorarioChart) {
      window._detalleHorarioChart.destroy();
      window._detalleHorarioChart = null;
    }

    var ctx = document.getElementById('detalleHorarioChart');
    if (!ctx) return;

    var dataEl = document.getElementById('detalle-horario-chart-data');
    if (!dataEl) return;

    var chartData;
    try {
      chartData = JSON.parse(dataEl.textContent || '{}');
    } catch (e) {
      return;
    }

    if (!chartData.labels || chartData.labels.length === 0) {
      ctx.parentElement.innerHTML =
        '<p class="text-gray-500 text-center py-8">No hay datos horarios para mostrar el gr\u00e1fico</p>';
      return;
    }

    var bandPlugin = {
      id: 'peakBands',
      beforeDraw: function (chart) {
        if (!chartData.bandas || chartData.bandas.length === 0) return;
        var ctx2 = chart.ctx;
        var chartArea = chart.chartArea;
        var meta = chart.getDatasetMeta(0);
        if (!meta || !meta.data || meta.data.length === 0) return;

        chartData.bandas.forEach(function (band) {
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
          ctx2.save();
          ctx2.fillStyle = isPM
            ? 'rgba(59, 130, 246, 0.15)'
            : 'rgba(251, 146, 60, 0.15)';
          ctx2.fillRect(x1, chartArea.top, x2 - x1, chartArea.bottom - chartArea.top);

          ctx2.fillStyle = isPM
            ? 'rgba(59, 130, 246, 0.7)'
            : 'rgba(251, 146, 60, 0.7)';
          ctx2.font = '10px sans-serif';
          ctx2.textAlign = 'left';
          ctx2.fillText(band.label, x1 + 4, chartArea.top + 12);
          ctx2.restore();
        });
      },
    };

    var hasMovil = chartData.hora_movil.some(function (v) { return v !== null; });
    var datasets = [
      {
        label: 'VEQ/15min',
        data: chartData.flujo_15min,
        backgroundColor: 'rgba(14, 165, 233, 0.6)',
        borderColor: 'rgba(14, 165, 233, 1)',
        borderWidth: 1,
        order: 2,
        yAxisID: 'y',
      },
    ];

    if (hasMovil) {
      datasets.push({
        label: 'Hora M\u00f3vil VEQ/h',
        data: chartData.hora_movil.map(function (v) { return v !== null ? v : null; }),
        type: 'line',
        borderColor: 'rgba(139, 92, 246, 1)',
        backgroundColor: 'rgba(139, 92, 246, 0.1)',
        borderWidth: 2,
        pointBackgroundColor: 'rgba(139, 92, 246, 1)',
        pointRadius: 3,
        pointHoverRadius: 5,
        fill: true,
        tension: 0.3,
        order: 1,
        yAxisID: 'y',
      });
    }

    window._detalleHorarioChart = new Chart(ctx, {
      type: 'bar',
      data: {
        labels: chartData.labels,
        datasets: datasets,
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        interaction: {
          mode: 'index',
          intersect: false,
        },
        scales: {
          y: {
            beginAtZero: true,
            title: { display: true, text: 'VEQ' },
            grid: { color: 'rgba(0,0,0,0.05)' },
          },
          x: {
            title: { display: true, text: 'Hora' },
            grid: { display: false },
            ticks: {
              maxRotation: 45,
              font: { size: 10 },
            },
          },
        },
        plugins: {
          legend: {
            position: 'top',
            labels: {
              usePointStyle: true,
              boxWidth: 12,
              padding: 16,
            },
          },
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
      },
      plugins: [bandPlugin],
    });
  };

  // Auto-render on initial page load
  if (document.readyState !== 'loading') {
    window.renderDetalleHorario();
  } else {
    document.addEventListener('DOMContentLoaded', window.renderDetalleHorario);
  }
})();
