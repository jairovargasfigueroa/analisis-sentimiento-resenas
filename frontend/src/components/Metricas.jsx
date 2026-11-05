import { useEffect, useState } from "react";
import { metricas as pedirMetricas } from "../api.js";
import { nombre } from "../formato.js";
import ComparacionModelos from "./ComparacionModelos.jsx";
import ErroresSeguros from "./ErroresSeguros.jsx";
import Experimentos from "./Experimentos.jsx";
import MatrizConfusion from "./MatrizConfusion.jsx";
import PalabrasInfluyentes from "./PalabrasInfluyentes.jsx";

// Pestaña Métricas: pide GET /metrics una vez y reparte metricas.json (contrato C6)
// entre componentes que solo muestran. No calcula métricas: vienen del entrenamiento.
export default function Metricas() {
  const [datos, setDatos] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => {
    pedirMetricas().then(setDatos).catch((e) => setError(e.message));
  }, []);

  if (error) return <p className="error">{error}</p>;
  if (!datos) return <p className="contador">Cargando métricas…</p>;

  const { modelo_produccion, criterio, justificacion, dataset, preprocesamiento } = datos;
  return (
    <>
      <section className="tarjeta">
        <h2>Modelo en producción: {nombre(modelo_produccion)}</h2>
        <p>{justificacion}</p>
        <small className="contador">
          Criterio: {criterio}. {dataset.n_train} noticias de entrenamiento y {dataset.n_test} de prueba ·
          {" "}{preprocesamiento.modo} · n-gramas ({preprocesamiento.ngram_range.join(",")})
        </small>
      </section>
      <ComparacionModelos modelos={datos.modelos} produccion={modelo_produccion} />
      <MatrizConfusion modelo={datos.modelos[modelo_produccion]} clave={modelo_produccion} />
      <Experimentos experimentos={datos.experimentos} preprocesamiento={preprocesamiento} />
      <PalabrasInfluyentes palabras={datos.palabras_influyentes} />
      <ErroresSeguros errores={datos.errores_ejemplo} />
    </>
  );
}
