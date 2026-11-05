// Lee en el navegador el archivo del lote y devuelve la lista de noticias.
// .txt: una noticia por línea. .csv: la columna "texto" (las celdas pueden tener comas,
// comillas y saltos de línea si van entre comillas, como las exporta Excel).

export async function leerNoticias(archivo) {
  const contenido = await archivo.text();
  if (archivo.name.toLowerCase().endsWith(".csv")) {
    const [encabezado, ...filas] = parsearCsv(contenido);
    const columna = (encabezado ?? []).map((c) => c.trim().toLowerCase()).indexOf("texto");
    if (columna === -1) throw new Error("El .csv necesita una columna llamada «texto».");
    return filas.map((f) => (f[columna] ?? "").trim()).filter(Boolean);
  }
  return contenido.split(/\r?\n/).map((l) => l.trim()).filter(Boolean);
}

// CSV mínimo: separa por comas fuera de comillas y entiende "" como una comilla escapada.
function parsearCsv(texto) {
  const filas = [];
  let fila = [], celda = "", enComillas = false;
  for (let i = 0; i < texto.length; i++) {
    const c = texto[i];
    if (enComillas) {
      if (c === '"' && texto[i + 1] === '"') { celda += '"'; i++; }
      else if (c === '"') enComillas = false;
      else celda += c;
    } else if (c === '"') enComillas = true;
    else if (c === ",") { fila.push(celda); celda = ""; }
    else if (c === "\n" || c === "\r") {
      if (c === "\r" && texto[i + 1] === "\n") i++;
      fila.push(celda); filas.push(fila); fila = []; celda = "";
    } else celda += c;
  }
  if (celda || fila.length) { fila.push(celda); filas.push(fila); }
  return filas;
}
