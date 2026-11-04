import { useEffect, useState } from "react";
import { health } from "../api.js";

// Consulta GET /health al cargar y cada 10 s: verde si el modelo cargó, rojo si no.
export default function Cabecera() {
  const [estado, setEstado] = useState({ clase: "", texto: "Conectando con la API…" });

  useEffect(() => {
    const consultar = () =>
      health()
        .then((r) => setEstado({ clase: "ok", texto: `API conectada · ${r.modelo}` }))
        .catch((e) => setEstado({ clase: "error", texto: e.message }));
    consultar();
    const intervalo = setInterval(consultar, 10000);
    return () => clearInterval(intervalo);
  }, []);

  return (
    <header className="cabecera">
      <h1>Detector de Noticias Falsas</h1>
      <span className="estado" role="status">
        <span className={`punto ${estado.clase}`} aria-hidden="true" />
        {estado.texto}
      </span>
    </header>
  );
}
