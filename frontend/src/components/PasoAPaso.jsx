// Muestra cada etapa del preprocesamiento que devuelve la API (contrato C5).
// No calcula nada: el preprocesamiento real está en src/nlp y viaja en la respuesta de /predict.

function Chips({ items, quitadas = new Set() }) {
  return (
    <div className="chips">
      {items.map((t, i) => (
        <span key={i} className={quitadas.has(t) ? "quitada" : ""}>{t}</span>
      ))}
    </div>
  );
}

export default function PasoAPaso({ pasos }) {
  const modo = { lema: "Lemas (spaCy)", stem: "Raíces (Snowball)", ninguno: "Sin reducir" }[pasos.modo];

  return (
    <section className="tarjeta">
      <h2>Preprocesamiento paso a paso</h2>
      <div className="paso">
        <h3>1 · Original</h3>
        <p>{pasos.original}</p>
      </div>
      <div className="paso">
        <h3>2 · Normalizado</h3>
        <p>{pasos.normalizado}</p>
      </div>
      <div className="paso">
        <h3>3 · Tokens ({pasos.tokens.length}) · tachadas las stop words</h3>
        <Chips items={pasos.tokens} quitadas={new Set(pasos.stopwords_eliminadas)} />
      </div>
      <div className="paso">
        <h3>4 · Sin stop words ({pasos.tokens_sin_stopwords.length})</h3>
        <Chips items={pasos.tokens_sin_stopwords} />
      </div>
      <div className="paso">
        <h3>5 · {modo}</h3>
        <Chips items={pasos.raices_o_lemas} />
      </div>
      <div className="paso">
        <h3>6 · Entrada a TF-IDF</h3>
        <p>{pasos.texto_final}</p>
      </div>
    </section>
  );
}
