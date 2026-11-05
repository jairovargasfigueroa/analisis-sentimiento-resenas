import { useState } from "react";
import Cabecera from "./components/Cabecera.jsx";
import Analizar from "./components/Analizar.jsx";
import Lote from "./components/Lote.jsx";
import Metricas from "./components/Metricas.jsx";

// Para agregar una pestaña basta sumar una línea aquí.
const PESTANAS = [
  { id: "analizar", nombre: "Analizar", Componente: Analizar },
  { id: "lote", nombre: "Lote", Componente: Lote },
  { id: "metricas", nombre: "Métricas", Componente: Metricas },
];

export default function App() {
  const [activa, setActiva] = useState(PESTANAS[0].id);
  const { Componente } = PESTANAS.find((p) => p.id === activa);

  return (
    <div className="contenedor">
      <Cabecera />
      <nav className="pestanas" role="tablist">
        {PESTANAS.map((p) => (
          <button key={p.id} role="tab" aria-selected={p.id === activa} onClick={() => setActiva(p.id)}>
            {p.nombre}
          </button>
        ))}
      </nav>
      <main role="tabpanel">
        <Componente />
      </main>
    </div>
  );
}
