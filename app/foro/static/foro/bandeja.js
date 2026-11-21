const bandeja = document.querySelector("#bandeja");
const cantidad = document.querySelector("#cantidad");
const lista = document.querySelector("#mensajes");
let ultimo = bandeja.dataset.ultimo || "";

async function actualizar() {
  if (document.hidden) return;
  try {
    const respuesta = await fetch(bandeja.dataset.url, {
      headers: { Accept: "application/json" }, cache: "no-store"
    });
    if (!respuesta.ok) return;
    const avisos = await respuesta.json();
    const nuevo = String(avisos[0]?.id ?? "");
    if (nuevo !== ultimo) document.querySelector("#actualizacion").hidden = false;
    ultimo = nuevo;
    cantidad.textContent = avisos.filter(aviso => !aviso.leida).length;
    const filas = avisos.slice(0, 30).map(aviso => {
      const fila = document.createElement("li");
      fila.textContent = (aviso.leida ? "" : "Nuevo · ") + aviso.mensaje;
      return fila;
    });
    if (filas.length) lista.replaceChildren(...filas);
  } catch {
    // Mantener la bandeja visible durante una interrupción de red.
  }
}

bandeja.addEventListener("toggle", () => { if (bandeja.open) actualizar(); });
window.setInterval(actualizar, 10000);
