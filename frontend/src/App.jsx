import { useState } from "react";
import Cabecera from "./components/Cabecera.jsx";

// Pestaña provisional hasta que exista el formulario de análisis.
const Analizar = () => <p>Próximamente: analizar una noticia.</p>;

// Para agregar una pestaña basta sumar una línea aquí.
const PESTANAS = [
  { id: "analizar", nombre: "Analizar", Componente: Analizar },
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
