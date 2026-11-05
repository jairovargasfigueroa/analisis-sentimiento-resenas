import { useState } from "react";
import { predecirLote } from "../api.js";
import { leerNoticias } from "../leerArchivo.js";
import ResultadosLote from "./ResultadosLote.jsx";

// El mismo límite que params.yaml -> api.max_textos_lote (la API vuelve a validarlo).
const MAX_NOTICIAS = 100;

// Pestaña Lote: sube un .csv o .txt, valida en el navegador y llama a POST /predict/lote.
export default function Lote() {
  const [noticias, setNoticias] = useState([]);
  const [nombre, setNombre] = useState("");
  const [respuesta, setRespuesta] = useState(null);
  const [error, setError] = useState("");
  const [cargando, setCargando] = useState(false);

  async function elegirArchivo(evento) {
    const archivo = evento.target.files[0];
    setRespuesta(null);
    setError("");
    setNoticias([]);
    if (!archivo) return;
    setNombre(archivo.name);
    try {
      const leidas = await leerNoticias(archivo);
      if (leidas.length === 0) throw new Error("El archivo no tiene noticias.");
      if (leidas.length > MAX_NOTICIAS) {
        throw new Error(`El archivo tiene ${leidas.length} noticias; el máximo es ${MAX_NOTICIAS}.`);
      }
      setNoticias(leidas);
    } catch (e) {
      setError(e.message);
    }
  }

  async function analizar() {
    setCargando(true);
    setError("");
    try {
      setRespuesta(await predecirLote(noticias));
    } catch (e) {
      setError(e.message);
    } finally {
      setCargando(false);
    }
  }

  return (
    <>
    <section className="tarjeta">
      <h2>Analizar varias noticias</h2>
      <p className="contador">
        Un <strong>.csv</strong> con una columna <code>texto</code>, o un <strong>.txt</strong> con una
        noticia por línea. Máximo {MAX_NOTICIAS}, cada una con al menos 20 palabras.{" "}
        <a href="/ejemplo_lote.csv" download>Descargar un ejemplo</a>.
      </p>
      <div className="fila">
        <input type="file" accept=".csv,.txt" aria-label="Archivo de noticias" onChange={elegirArchivo} />
        <span className="contador">{noticias.length > 0 && `${nombre}: ${noticias.length} noticias`}</span>
        <button className="primario" onClick={analizar} disabled={noticias.length === 0 || cargando}>
          {cargando ? "Analizando…" : "Analizar lote"}
        </button>
      </div>
      {error && <p className="error" role="alert">{error}</p>}
    </section>
    {respuesta && <ResultadosLote respuesta={respuesta} />}
    </>
  );
}
