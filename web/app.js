(function () {
  "use strict";

  let listaPruebasActuales = [];
  let filtroActual = "todos";

  const btnEjecutar = document.getElementById("btn-ejecutar-tests");
  const indicadorEjecucion = document.getElementById("indicador-ejecucion");
  const alertaError = document.getElementById("alerta-error");
  const mensajeError = document.getElementById("mensaje-error");
  const estadoVacio = document.getElementById("estado-vacio-pruebas");
  const contenedorResultados = document.getElementById("contenedor-resultados");

  const elTotal = document.getElementById("resumen-total");
  const elAprobados = document.getElementById("resumen-aprobados");
  const elFallidos = document.getElementById("resumen-fallidos");
  const elOmitidos = document.getElementById("resumen-omitidos");
  const elErrores = document.getElementById("resumen-errores");
  const elDuracion = document.getElementById("resumen-duracion");
  const elCodigo = document.getElementById("resumen-codigo");
  const elHora = document.getElementById("resumen-hora");

  const cuentaTodos = document.getElementById("cuenta-filtro-todos");
  const cuentaFallidos = document.getElementById("cuenta-filtro-fallidos");
  const cuentaAprobados = document.getElementById("cuenta-filtro-aprobados");

  const cuerpoTabla = document.getElementById("cuerpo-tabla-pruebas");
  const bloqueConsola = document.getElementById("bloque-consola");
  const btnCopiarConsola = document.getElementById("btn-copiar-consola");

  const btnCopiarSustentacion = document.getElementById("btn-copiar-sustentacion");
  const avisoCopiado = document.getElementById("aviso-copiado");

  function renderizarTextoConCodigo(contenedor, texto) {
    const partes = texto.split("`");
    for (let i = 0; i < partes.length; i++) {
      if (i % 2 === 1) {
        const elCodigo = document.createElement("code");
        elCodigo.textContent = partes[i];
        contenedor.appendChild(elCodigo);
      } else if (partes[i]) {
        contenedor.appendChild(document.createTextNode(partes[i]));
      }
    }
  }

  async function cargarTareas() {
    const cargandoEl = document.getElementById("cargando-tareas");
    const listaEl = document.getElementById("lista-tareas");

    try {
      const resp = await fetch("/api/tasks");
      if (!resp.ok) {
        throw new Error(`HTTP ${resp.status}`);
      }
      const datos = await resp.json();
      if (!datos.ok || !Array.isArray(datos.tasks)) {
        throw new Error("Formato inválido en respuesta de tareas");
      }

      listaEl.replaceChildren();
      datos.tasks.forEach((tarea, indice) => {
        const li = document.createElement("li");
        li.className = "item-tarea";

        const badge = document.createElement("span");
        badge.className = "numero-tarea";
        badge.textContent = String(indice + 1);

        const textoDiv = document.createElement("div");
        textoDiv.className = "texto-tarea";
        renderizarTextoConCodigo(textoDiv, tarea);

        li.appendChild(badge);
        li.appendChild(textoDiv);
        listaEl.appendChild(li);
      });

      cargandoEl.style.display = "none";
      listaEl.style.display = "flex";
    } catch (err) {
      cargandoEl.textContent = "No se pudieron cargar las tareas desde el README (" + err.message + ").";
      cargandoEl.style.color = "var(--color-error)";
    }
  }

  async function ejecutarTests() {
    btnEjecutar.disabled = true;
    indicadorEjecucion.style.display = "flex";
    alertaError.style.display = "none";

    try {
      const resp = await fetch("/api/tests", {
        method: "POST",
        headers: { "Content-Type": "application/json" }
      });

      const datos = await resp.json();
      if (!resp.ok && !datos) {
        throw new Error(`Error en el servidor: HTTP ${resp.status}`);
      }

      if (datos.error && (!datos.tests || datos.tests.length === 0)) {
        throw new Error(datos.error);
      }

      actualizarResultados(datos);
    } catch (err) {
      alertaError.style.display = "block";
      mensajeError.textContent = err.message || "Error al ejecutar pytest.";
    } finally {
      btnEjecutar.disabled = false;
      indicadorEjecucion.style.display = "none";
    }
  }

  function actualizarResultados(datos) {
    estadoVacio.style.display = "none";
    contenedorResultados.style.display = "block";

    const resumen = datos.summary || {
      total: 0,
      passed: 0,
      failed: 0,
      skipped: 0,
      errors: 0,
      duration: 0
    };

    elTotal.textContent = String(resumen.total);
    elAprobados.textContent = String(resumen.passed);
    elFallidos.textContent = String(resumen.failed);
    elOmitidos.textContent = String(resumen.skipped);
    elErrores.textContent = String(resumen.errors);

    const dur = typeof resumen.duration === "number" ? resumen.duration.toFixed(2) + "s" : String(resumen.duration);
    elDuracion.textContent = dur;

    elCodigo.textContent = String(datos.exit_code);
    if (datos.exit_code === 0) {
      elCodigo.style.color = "var(--color-exito)";
      elCodigo.style.borderColor = "var(--color-exito)";
    } else {
      elCodigo.style.color = "var(--color-error)";
      elCodigo.style.borderColor = "var(--color-error)";
    }

    const ahora = new Date();
    elHora.textContent = ahora.toLocaleTimeString();

    listaPruebasActuales = Array.isArray(datos.tests) ? datos.tests : [];

    cuentaTodos.textContent = String(listaPruebasActuales.length);
    cuentaFallidos.textContent = String(listaPruebasActuales.filter(t => t.outcome === "failed" || t.outcome === "error").length);
    cuentaAprobados.textContent = String(listaPruebasActuales.filter(t => t.outcome === "passed").length);

    renderizarTablaPruebas();

    let consolaTexto = datos.stdout || "";
    if (datos.stderr && datos.stderr.trim()) {
      consolaTexto += "\n\n--- STDERR ---\n" + datos.stderr;
    }
    bloqueConsola.textContent = consolaTexto || "(Sin salida en consola)";
  }

  function renderizarTablaPruebas() {
    cuerpoTabla.replaceChildren();

    const filtrados = listaPruebasActuales.filter(t => {
      if (filtroActual === "failed") {
        return t.outcome === "failed" || t.outcome === "error";
      }
      if (filtroActual === "passed") {
        return t.outcome === "passed";
      }
      return true;
    });

    if (filtrados.length === 0) {
      const filaVacia = document.createElement("tr");
      const celda = document.createElement("td");
      celda.colSpan = 5;
      celda.style.textAlign = "center";
      celda.style.color = "var(--texto-secundario)";
      celda.style.padding = "24px";
      celda.textContent = "No hay pruebas que coincidan con el filtro seleccionado.";
      filaVacia.appendChild(celda);
      cuerpoTabla.appendChild(filaVacia);
      return;
    }

    filtrados.forEach((test, idx) => {
      const tr = document.createElement("tr");
      tr.className = "fila-prueba";

      const tdEstado = document.createElement("td");
      const insignia = document.createElement("span");
      insignia.className = "insignia-estado";

      if (test.outcome === "passed") {
        insignia.classList.add("estado-paso");
        insignia.textContent = "PASÓ";
      } else if (test.outcome === "failed" || test.outcome === "error") {
        insignia.classList.add("estado-fallo");
        insignia.textContent = test.outcome === "error" ? "ERROR" : "FALLÓ";
      } else {
        insignia.classList.add("estado-omitido");
        insignia.textContent = "OMITIDO";
      }
      tdEstado.appendChild(insignia);
      tr.appendChild(tdEstado);

      const tdNombre = document.createElement("td");
      const spanNombre = document.createElement("span");
      spanNombre.className = "nombre-test";
      spanNombre.textContent = test.name || test.nodeid;
      tdNombre.appendChild(spanNombre);

      if (test.message && (test.outcome === "failed" || test.outcome === "error")) {
        const divError = document.createElement("div");
        divError.className = "resumen-error";
        divError.textContent = test.message;
        tdNombre.appendChild(divError);
      }
      tr.appendChild(tdNombre);

      const tdArchivo = document.createElement("td");
      tdArchivo.className = "archivo-test";
      tdArchivo.textContent = test.file || "-";
      tr.appendChild(tdArchivo);

      const tdDuracion = document.createElement("td");
      tdDuracion.className = "duracion-test";
      tdDuracion.textContent = typeof test.duration === "number" ? test.duration.toFixed(3) + "s" : "-";
      tr.appendChild(tdDuracion);

      const tdDetalle = document.createElement("td");
      if (test.traceback && test.traceback.trim()) {
        const btnDetalle = document.createElement("button");
        btnDetalle.type = "button";
        btnDetalle.className = "btn-detalle";
        btnDetalle.textContent = "Ver traza";
        const idDetalle = "traza-" + idx;

        btnDetalle.addEventListener("click", () => {
          const filaDetalle = document.getElementById(idDetalle);
          if (filaDetalle) {
            const visible = filaDetalle.style.display !== "none";
            filaDetalle.style.display = visible ? "none" : "table-row";
            btnDetalle.textContent = visible ? "Ver traza" : "Ocultar";
          }
        });
        tdDetalle.appendChild(btnDetalle);
      } else {
        tdDetalle.textContent = "—";
      }
      tr.appendChild(tdDetalle);

      cuerpoTabla.appendChild(tr);

      if (test.traceback && test.traceback.trim()) {
        const trDetalle = document.createElement("tr");
        trDetalle.className = "fila-detalle";
        trDetalle.id = "traza-" + idx;
        trDetalle.style.display = "none";

        const tdContenido = document.createElement("td");
        tdContenido.colSpan = 5;

        const preTraza = document.createElement("pre");
        preTraza.className = "traza-detalle";
        preTraza.textContent = test.traceback;

        tdContenido.appendChild(preTraza);
        trDetalle.appendChild(tdContenido);
        cuerpoTabla.appendChild(trDetalle);
      }
    });
  }

  function configurarFiltros() {
    const botones = document.querySelectorAll(".btn-filtro");
    botones.forEach(btn => {
      btn.addEventListener("click", () => {
        botones.forEach(b => b.classList.remove("activo"));
        btn.classList.add("activo");
        filtroActual = btn.getAttribute("data-filtro") || "todos";
        renderizarTablaPruebas();
      });
    });
  }

  function copiarTexto(texto) {
    if (navigator.clipboard && navigator.clipboard.writeText) {
      return navigator.clipboard.writeText(texto);
    }
    const tempInput = document.createElement("textarea");
    tempInput.value = texto;
    document.body.appendChild(tempInput);
    tempInput.select();
    document.execCommand("copy");
    document.body.removeChild(tempInput);
    return Promise.resolve();
  }

  function configurarAcciones() {
    btnEjecutar.addEventListener("click", ejecutarTests);

    btnCopiarConsola.addEventListener("click", () => {
      copiarTexto(bloqueConsola.textContent).then(() => {
        btnCopiarConsola.textContent = "¡Copiado!";
        setTimeout(() => {
          btnCopiarConsola.textContent = "Copiar consola";
        }, 1800);
      });
    });

    btnCopiarSustentacion.addEventListener("click", () => {
      const veredicto = document.querySelector('input[name="veredicto"]:checked')?.value || "No especificado";
      const pruebasRespaldo = document.getElementById("campo-pruebas-respaldo").value.trim();
      const flujoVerificado = document.getElementById("campo-flujo-verificado").value.trim();
      const esperadoObservado = document.getElementById("campo-esperado-observado").value.trim();

      const total = elTotal.textContent || "0";
      const aprobados = elAprobados.textContent || "0";
      const fallidos = elFallidos.textContent || "0";
      const codigoSalida = elCodigo.textContent || "-";

      const reporte = [
        "# Sustentación de Ejercicio: Préstamos de Biblioteca (AIS86)",
        "",
        `**Diagnóstico General:** ${veredicto}`,
        `**Estado de Pruebas:** Total: ${total} | Aprobados: ${aprobados} | Fallidos: ${fallidos} (Código: ${codigoSalida})`,
        "",
        "## 1. Pruebas que respaldan la conclusión",
        pruebasRespaldo || "(Sin respuesta ingresada)",
        "",
        "## 2. Flujo de datos verificado",
        flujoVerificado || "(Sin respuesta ingresada)",
        "",
        "## 3. Resultado esperado vs observado",
        esperadoObservado || "(Sin respuesta ingresada)",
        "",
        `*Generado el ${new Date().toLocaleString()} desde la interfaz local AIS86.*`
      ].join("\n");

      copiarTexto(reporte).then(() => {
        avisoCopiado.style.display = "inline";
        setTimeout(() => {
          avisoCopiado.style.display = "none";
        }, 2500);
      });
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    cargarTareas();
    configurarFiltros();
    configurarAcciones();
  });
})();
