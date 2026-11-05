import { pct } from "../formato.js";

// Los errores en que el modelo estaba más seguro (conjunto de prueba).
// La explicación de cada uno está en el notebook y en el informe (sección 6).
export default function ErroresSeguros({ errores }) {
  return (
    <section className="tarjeta">
      <h2>Errores con mayor confianza</h2>
      <div className="errores">
        {errores.map((e, i) => (
          <article key={i} className="error-item">
            <div className="fila">
              <span className={`etiqueta ${e.real}`}>real: {e.real}</span>
              <span className={`etiqueta ${e.predicho}`}>predicho: {e.predicho} · {pct(e.probabilidad)}</span>
              <span className="contador">{e.tema} · {e.fuente} · {e.anio}</span>
            </div>
            <p>{e.texto}…</p>
          </article>
        ))}
      </div>
      <small className="contador">
        Patrón: falla cuando el estilo engaña (falsas bien redactadas, verdaderas sobre temas que suelen
        ser bulos). El modelo juzga cómo está escrita la noticia, no si es verdad.
      </small>
    </section>
  );
}
