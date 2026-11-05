import { nombre, pct } from "../formato.js";

// Matriz de confusión 2×2 del modelo en producción y sus métricas por clase.
// Filas = clase real, columnas = clase predicha. La intensidad del color es la proporción
// de la fila: la diagonal (aciertos) debería ser la más intensa.
export default function MatrizConfusion({ modelo, clave }) {
  const { matriz_confusion: matriz, etiquetas, por_clase: porClase } = modelo;

  return (
    <section className="tarjeta">
      <h2>Matriz de confusión · {nombre(clave)}</h2>
      <table className="matriz">
        <thead>
          <tr>
            <th />
            {etiquetas.map((e) => <th key={e}>predicho {e}</th>)}
          </tr>
        </thead>
        <tbody>
          {matriz.map((fila, i) => {
            const total = fila.reduce((a, b) => a + b, 0);
            return (
              <tr key={etiquetas[i]}>
                <th>real {etiquetas[i]}</th>
                {fila.map((n, j) => (
                  <td key={j} className={i === j ? "acierto" : "fallo"}
                      style={{ "--intensidad": total ? n / total : 0 }}>
                    <strong>{n}</strong>
                    <small>{pct(total ? n / total : 0)}</small>
                  </td>
                ))}
              </tr>
            );
          })}
        </tbody>
      </table>

      <h3 className="subtitulo">Métricas por clase (prueba)</h3>
      <table className="tabla">
        <thead>
          <tr><th>Clase</th><th>Precision</th><th>Recall</th><th>F1</th><th>Noticias</th></tr>
        </thead>
        <tbody>
          {etiquetas.map((e) => (
            <tr key={e}>
              <td>{e}</td>
              <td>{pct(porClase[e].precision)}</td>
              <td>{pct(porClase[e].recall)}</td>
              <td>{pct(porClase[e].f1)}</td>
              <td>{porClase[e].soporte}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <small className="contador">
        Recall de «falsa»: de las noticias falsas, cuántas detecta. Las que no detecta pasan como
        verdaderas (celda roja de la primera fila): es el error más costoso.
      </small>
    </section>
  );
}
