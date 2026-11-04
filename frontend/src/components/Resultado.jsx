// Clase predicha con su color y la probabilidad como barra.
export default function Resultado({ resultado }) {
  const { clase, probabilidad, probabilidades, modelo } = resultado;
  const porcentaje = Math.round(probabilidad * 100);

  return (
    <section className={`resultado ${clase}`} aria-live="polite">
      <div className="clase">
        {clase === "falsa" ? "Parece falsa" : "Parece verdadera"} · {porcentaje} %
      </div>
      <div className="barra" role="img" aria-label={`Probabilidad ${porcentaje} %`}>
        <div style={{ width: `${porcentaje}%` }} />
      </div>
      <small>
        Falsa {Math.round(probabilidades.falsa * 100)} % · Verdadera {Math.round(probabilidades.verdadera * 100)} % ·
        modelo: {modelo}. El modelo juzga el estilo del texto, no verifica los hechos.
      </small>
    </section>
  );
}
