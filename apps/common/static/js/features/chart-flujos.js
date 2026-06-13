(function() {
  if (window._flujosChart) {
    window._flujosChart.destroy();
    window._flujosChart = null;
  }
  var ctx = document.getElementById('flujosChart');
  if (!ctx) return;
  var chartDataEl = document.getElementById('chart-data');
  if (!chartDataEl) return;
  var chartData;
  try { chartData = JSON.parse(chartDataEl.textContent || '{}'); } catch(e) { return; }
  if (!chartData || !chartData.labels || chartData.labels.length === 0) {
    ctx.parentElement.innerHTML = '<p class="text-gray-500 text-center py-4">No hay datos suficientes para mostrar el gr\u00e1fico</p>';
    return;
  }
  window._flujosChart = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: chartData.labels,
      datasets: chartData.datasets.map(function(ds) {
        return {
          label: ds.label,
          data: ds.data,
          backgroundColor: ds.backgroundColor || 'rgba(99, 102, 241, 0.6)',
          borderColor: ds.borderColor || 'rgba(99, 102, 241, 1)',
          borderWidth: 1
        };
      })
    },
    options: {
      responsive: true, maintainAspectRatio: false,
      scales: {
        y: { beginAtZero: true, title: { display: true, text: 'Flujo Total (FTOT)' } },
        x: { title: { display: true, text: 'Punto de Control' } }
      },
      plugins: { legend: { position: 'top' } }
    }
  });
})();
