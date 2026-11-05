// Formato de los datos de metricas.json para mostrarlos en la pestaña Métricas.

const NOMBRES = { baseline: "Línea base", regresion_logistica: "Regresión logística", naive_bayes: "Naive Bayes" };

// "regresion_logistica" -> "Regresión logística"
export const nombre = (clave) => NOMBRES[clave] ?? clave;

// 0.7733 -> "77.3 %"
export const pct = (x) => (x == null ? "—" : `${(x * 100).toFixed(1)} %`);
