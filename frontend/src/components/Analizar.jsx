import { useState } from "react";
import { predecir } from "../api.js";
import { EJEMPLOS } from "../ejemplos.js";
import PasoAPaso from "./PasoAPaso.jsx";
import Resultado from "./Resultado.jsx";

// Los mismos límites que params.yaml -> api (la API vuelve a validarlos).
const MIN_PALABRAS = 20;
const MAX_CARACTERES = 20000;

export default function Analizar() {
  const [texto, setTexto] = useState("");
  const [resultado, setResultado] = useState(null);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  const palabras = texto.trim() ? texto.trim().split(/\s+/).length : 0;
  const valido = palabras >= MIN_PALABRAS && texto.length <= MAX_CARACTERES;

  async function analizar() {
    setCargando(true);
    setError("");
    try {
      setResultado(await predecir(texto));
    } catch (e) {
      setResultado(null);
      setError(e.message);
    } finally {
      setCargando(false);
    }
  }

  return (
    <>
      <section className="tarjeta">
        <h2>Pega una noticia (titular y cuerpo)</h2>
        <div className="fila" style={{ marginTop: 0, marginBottom: 8 }}>
          {EJEMPLOS.map((e) => (
            <button key={e.nombre} className="ejemplo" onClick={() => { setTexto(e.texto); setResultado(null); }}>
              {e.nombre}
            </button>
          ))}
        </div>
        <textarea
          aria-label="Texto de la noticia"
          value={texto}
          onChange={(e) => setTexto(e.target.value)}
          placeholder="Escribe o pega aquí la noticia…"
        />
        <div className="fila">
          <span className={`contador ${texto && !valido ? "mal" : ""}`}>
            {palabras} palabras (mínimo {MIN_PALABRAS}) · {texto.length.toLocaleString("es")} / {MAX_CARACTERES.toLocaleString("es")} caracteres
          </span>
          <button className="primario" onClick={analizar} disabled={!valido || cargando}>
            {cargando ? "Analizando…" : "Analizar"}
          </button>
        </div>
        {error && <p className="error" role="alert">{error}</p>}
      </section>
      {resultado && <Resultado resultado={resultado} />}
      {resultado && <PasoAPaso pasos={resultado.preprocesamiento} />}
    </>
  );
}
