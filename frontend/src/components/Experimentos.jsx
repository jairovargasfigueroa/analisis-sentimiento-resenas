import { pct } from "../formato.js";

// Efecto de cada decisión de NLP (E1, E2) y la prueba en otra época (E3).
// E1 y E2: mismo modelo, cambia un solo parámetro, F1 de validación cruzada en train.
const DESCRIPCION = {
  stem_vs_lema: { titulo: "E1 · Stemming vs lematización", parametro: "nlp.modo" },
  ngramas: { titulo: "E2 · Unigramas vs unigramas + bigramas", parametro: "tfidf.ngram_range" },
};

export default function Experimentos({ experimentos, preprocesamiento }) {
  const elegido = {
    stem_vs_lema: preprocesamiento.modo,
    ngramas: `(${preprocesamiento.ngram_range.join(",")})`,
  };
  const temporal = experimentos.temporal && Object.entries(experimentos.temporal)[0];

  return (
    <section className="tarjeta">
      <h2>Efecto de cada decisión</h2>
      {Object.entries(DESCRIPCION).map(([clave, { titulo, parametro }]) => (
        <div key={clave} className="experimento">
          <h3 className="subtitulo">{titulo} <code>{parametro}</code></h3>
          {Object.entries(experimentos[clave]).map(([opcion, r]) => (
            <div key={opcion} className="barra-fila">
              <span>{opcion}{opcion === elegido[clave] && " ★"}</span>
              <div className="barra">
                <div className={opcion === elegido[clave] ? "prod" : ""} style={{ width: pct(r.f1_macro).replace(" ", "") }} />
              </div>
              <span>{pct(r.f1_macro)}</span>
            </div>
          ))}
        </div>
      ))}
      {temporal && (
        <div className="experimento">
          <h3 className="subtitulo">E3 · Otra época: entrenar con {temporal[0].replace("->", "y probar con")}</h3>
          <p>
            F1 macro <strong>{pct(temporal[1].f1_macro)}</strong> ({temporal[1].n_train} noticias de
            entrenamiento, {temporal[1].n_test} de prueba). Cae porque la v2 está dominada por el
            COVID-19, que no existía en 2018: el modelo aprende el estilo y los temas de una época.
          </p>
        </div>
      )}
      <small className="contador">★ configuración en producción. F1 macro de validación cruzada (E1 y E2).</small>
    </section>
  );
}
