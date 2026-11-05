// Todas las llamadas HTTP a la API (contrato C8) están en este archivo.
const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function pedir(ruta, opciones) {
  let respuesta;
  try {
    respuesta = await fetch(`${BASE}${ruta}`, opciones);
  } catch {
    throw new Error("No se pudo conectar con la API. ¿Está corriendo uvicorn?");
  }
  const cuerpo = await respuesta.json();
  // La API usa un formato de error único: {"error": {"codigo", "mensaje"}}.
  if (!respuesta.ok) {
    const sinModelo = cuerpo.modelo_cargado === false && "La API está activa, pero no hay modelo entrenado.";
    throw new Error(cuerpo.error?.mensaje ?? (sinModelo || `Error ${respuesta.status}`));
  }
  return cuerpo;
}

export const health = () => pedir("/health");

export const predecir = (texto) =>
  pedir("/predict", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ texto }),
  });

export const metricas = () => pedir("/metrics");

export const predecirLote = (textos) =>
  pedir("/predict/lote", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ textos }),
  });
