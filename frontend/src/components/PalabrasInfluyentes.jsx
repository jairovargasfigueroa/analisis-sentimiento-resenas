// Los términos (lematizados) con más peso hacia cada clase en el modelo de producción.
// El ancho de la barra es el peso relativo al mayor de los dos lados.
export default function PalabrasInfluyentes({ palabras }) {
  const clases = Object.keys(palabras);
  const maximo = Math.max(...clases.flatMap((c) => palabras[c].map((p) => Math.abs(p.peso))));

  return (
    <section className="tarjeta">
      <h2>Palabras más influyentes</h2>
      <div className="columnas">
        {clases.map((clase) => (
          <div key={clase}>
            <h3 className="subtitulo">empujan hacia «{clase}»</h3>
            {palabras[clase].map(({ termino, peso }) => (
              <div key={termino} className="barra-fila corta">
                <span>{termino}</span>
                <div className="barra">
                  <div className={clase} style={{ width: `${(Math.abs(peso) / maximo) * 100}%` }} />
                </div>
                <span>{Math.abs(peso).toFixed(2)}</span>
              </div>
            ))}
          </div>
        ))}
      </div>
      <small className="contador">
        Coeficientes de la regresión logística. Pesan el estilo (cifras, días, exclamaciones) y también
        algunos temas que en este corpus abundan en bulos: es un sesgo del corpus, no una regla general.
      </small>
    </section>
  );
}
