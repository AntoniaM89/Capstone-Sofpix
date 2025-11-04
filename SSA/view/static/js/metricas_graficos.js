document.addEventListener("DOMContentLoaded", () => {
  const metricData = window.metricData || {};
  const safeArray = v => Array.isArray(v) ? v : [];

  let chartAsignaturas = null;
  let chartProfesores = null;

  function crearGraficoSeguro(canvasId, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return null;
    try {
      return new Chart(canvas, config);
    } catch (err) {
      console.error("Error al crear chart en", canvasId, err);
      return null;
    }
  }

  function renderCharts(asignaturas, profesores) {
    // ============================
    // 1) Promedio por asignaturas
    // ============================
    const asigArray = safeArray(asignaturas);
    const etiquetas = asigArray.map(a => a.codigo || a.nombre_asi || "Sin nombre");
    const valores = asigArray.map(a => Number(a.promedio) || 0);
    const colores = valores.map(v => v > 5.4 ? "#4caf50" : v > 3.9 ? "#ff9800" : "#f44336");

    if (chartAsignaturas) chartAsignaturas.destroy();
    if (etiquetas.length > 0) {
      chartAsignaturas = crearGraficoSeguro("chartAsignaturasCurso", {
        type: "bar",
        data: { labels: etiquetas, datasets: [{ label: "Promedio por Asignatura", data: valores, backgroundColor: colores }] },
        options: {
          responsive: true,
          plugins: { legend: { display: false } },
          scales: { y: { beginAtZero: true, max: 7 }, x: { ticks: { align: 'center', autoSkip: false, maxRotation:0, minRotation:0 } } }
        }
      });
    }

    // ============================
    // 2) Promedio por profesor
    // ============================
    const profArray = profesores;
    if (chartProfesores) chartProfesores.destroy();

    if (profArray !== null && profArray !== undefined) {
      if (typeof profArray === "number") {
        const color = profArray > 5.5 ? "#4caf50" : profArray > 4.5 ? "#ff9800" : "#f44336";
        chartProfesores = crearGraficoSeguro("chartPromedioProfesor", {
          type: "bar",
          data: { labels: ["Profesor"], datasets: [{ label: "Promedio", data: [profArray], backgroundColor: color }] },
          options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 7 } } }
        });
      } else if (Array.isArray(profArray)) {
        const labels = profArray.map(p => p.profe || p.nombre || "Desconocido");
        const valores = profArray.map(p => Number(p.promedio) || 0);
        const colores = valores.map(v => v > 5.5 ? "#4caf50" : v > 4.5 ? "#ff9800" : "#f44336");

        chartProfesores = crearGraficoSeguro("chartPromedioProfesor", {
          type: "bar",
          data: { labels, datasets: [{ label: "Promedio por Profesor", data: valores, backgroundColor: colores }] },
          options: { responsive: true, plugins: { legend: { display: false } }, scales: { y: { beginAtZero: true, max: 7 } } }
        });
      }
    }
  }

  // Render inicial con datos de la carga de página
  renderCharts(metricData.asignaturas_promedio, metricData.promedio_profesor);

  // Exponer globalmente para actualizar desde actualizarFiltros()
  window.updateMetricasCharts = renderCharts;
});
