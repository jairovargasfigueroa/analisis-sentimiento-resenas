import { pct } from "../formato.js";

// Resumen por clase (barra apilada) y tabla con la clase y probabilidad de cada noticia.
export default function ResultadosLote({ respuesta }) {
  const { resultados, resumen } = respuesta;
  const total = resultados.length;

  return (
    <section className="tarjeta">
      <h2>Resultados · {total} noticias</h2>
      <div className="resumen-lote">
        {Object.entries(resumen).map(([clase, n]) => (
          <span key={clase} className={`etiqueta ${clase}`}>{n} {clase}{n === 1 ? "" : "s"} · {pct(n / total)}</span>
        ))}
      </div>
      <div className="barra apilada" role="img"
           aria-label={Object.entries(resumen).map(([c, n]) => `${n} ${c}`).join(", ")}>
        {Object.entries(resumen).map(([clase, n]) => (
          <div key={clase} className={clase} style={{ width: `${(n / total) * 100}%` }} />
        ))}
      </div>

      <div className="tabla-scroll">
        <table className="tabla lote">
          <thead>
            <tr><th>#</th><th>Noticia</th><th>Clase</th><th>Probabilidad</th></tr>
          </thead>
          <tbody>
            {resultados.map((r, i) => (
              <tr key={i}>
                <td>{i + 1}</td>
                <td className="texto-corto" title={r.texto}>{r.texto.slice(0, 120)}{r.texto.length > 120 && "…"}</td>
                <td><span className={`etiqueta ${r.clase}`}>{r.clase}</span></td>
                <td>{pct(r.probabilidad)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <small className="contador">El modelo juzga el estilo del texto, no verifica los hechos.</small>
    </section>
  );
}
