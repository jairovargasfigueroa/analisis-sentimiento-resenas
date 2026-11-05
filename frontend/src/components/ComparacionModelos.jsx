import { nombre, pct } from "../formato.js";

// Tabla de la línea base y los dos modelos, más barras de F1 en prueba.
// Las barras son divs con ancho en %: para 3 valores no hace falta una librería de gráficos.
export default function ComparacionModelos({ modelos, produccion }) {
  const filas = Object.entries(modelos);

  return (
    <section className="tarjeta">
      <h2>Comparación de modelos</h2>
      <div className="tabla-scroll">
        <table className="tabla">
          <thead>
            <tr>
              <th>Modelo</th>
              <th title="Validación cruzada de 5 particiones sobre train: con esto se elige">F1 CV</th>
              <th>Accuracy</th>
              <th>Precision</th>
              <th>Recall</th>
              <th>F1 prueba</th>
              <th>Hiperparámetros</th>
            </tr>
          </thead>
          <tbody>
            {filas.map(([clave, m]) => (
              <tr key={clave} className={clave === produccion ? "destacada" : ""}>
                <td>{nombre(clave)}{clave === produccion && " ★"}</td>
                <td>{m.f1_cv_media == null ? "—" : `${pct(m.f1_cv_media)} ± ${pct(m.f1_cv_std)}`}</td>
                <td>{pct(m.accuracy)}</td>
                <td>{pct(m.precision_macro)}</td>
                <td>{pct(m.recall_macro)}</td>
                <td>{pct(m.f1_macro)}</td>
                <td>{m.mejores_hiperparametros ? Object.entries(m.mejores_hiperparametros)
                  .map(([k, v]) => `${k.replace("clf__", "")}=${v}`).join(", ") : "—"}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <h3 className="subtitulo">F1 macro en prueba</h3>
      {filas.map(([clave, m]) => (
        <div key={clave} className="barra-fila">
          <span>{nombre(clave)}</span>
          <div className="barra"><div className={clave === produccion ? "prod" : ""} style={{ width: pct(m.f1_macro).replace(" ", "") }} /></div>
          <span>{pct(m.f1_macro)}</span>
        </div>
      ))}
      <small className="contador">
        ★ en producción. Se elige por F1 de validación cruzada; la prueba solo confirma.
      </small>
    </section>
  );
}
