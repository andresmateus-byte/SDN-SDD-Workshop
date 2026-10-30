# Registro de ingeniería de prompts — Sesión 1

Este archivo es una plantilla de trazabilidad para los seis documentos de especificación. Para que constituya evidencia académica, el equipo debe sustituir/confirmar los textos con los prompts que realmente utilizó en la sesión 1 y registrar las salidas observadas. No presentar los ejemplos de abajo como transcripciones literales si no lo fueron.

## Técnicas exigidas

- **Contextual framing:** explicar que es una simulación SDN a nivel de aplicación con dos procesos REST/JSON, fuera de OpenFlow de producción.
- **Structured prompting:** pedir IDs de requisitos, criterios de aceptación, entradas, salidas y errores.
- **Role prompting:** solicitar revisión desde roles distintos (analista, arquitecto, revisor de API y tester).
- **Few-shot:** incluir ejemplos concretos de la topología A-B-D / A-C-D y costos esperados.
- **Iterative refinement:** pedir ambigüedades, evaluar las sugerencias y registrar las decisiones humanas.

## Prompts de referencia y revisión

### P1 — Requisitos

**Prompt de referencia:** Actúa como analista de requisitos. Especifica la solución Controller/Router del taller; separa FR y NFR, usa IDs trazables, incluye condiciones de error y criterios verificables. No generes código. Identifica al menos tres ambigüedades.

**Crítica/decisiones que debe confirmar el equipo:** distinguir `NODE_NOT_FOUND` de `PATH_NOT_FOUND`; cerrar las fórmulas de costo; definir qué ocurre cuando el Controller no responde. Verificar que estas decisiones estén reflejadas en `01-requirements.md`.

**Prompt real / salida / corrección / responsable:** [completar con evidencia real].

### P2 — Arquitectura estática

**Prompt de referencia:** Como arquitecto de software, propone diagramas de componentes y clases para dos procesos separados. Muestra MVC, servicios de dominio, interfaces DAO, implementaciones concretas e inyección de dependencias en ambas aplicaciones. No ubiques Dijkstra ni forwarding dentro de endpoints.

**Crítica/decisiones que debe confirmar el equipo:** cada clase de las secuencias debe existir en la arquitectura estática; el Router no debe tener algoritmo de ruta; servicios no acceden directamente a archivos.

**Prompt real / salida / corrección / responsable:** [completar con evidencia real].

### P3 — Arquitectura dinámica

**Prompt de referencia:** Genera tres diagramas de secuencia coherentes con las clases y API: forwarding exitoso, falla/restauración de enlace y Controller no disponible. Incluye validación, DAO, respuesta HTTP y errores controlados. No agregues endpoints fuera del contrato.

**Crítica/decisiones que debe confirmar el equipo:** las interacciones deben corresponder a métodos existentes; el estado de enlaces cambia en Controller y la ruta del Router proviene del Controller.

**Prompt real / salida / corrección / responsable:** [completar con evidencia real].

### P4 — Contrato API (few-shot)

**Prompt de referencia:** Define request/response JSON para `GET /topology`, `GET /route`, `POST /links/fail`, `POST /links/restore`, `POST /packets` y `GET /health`. Usa como ejemplo la ruta A-B-D de costo delay 20 y, al fallar B-D, A-C-D de costo 35. Incluye 400, 404, 500 y 503 según su semántica.

**Crítica/decisiones que debe confirmar el equipo:** campos snake_case; no mezclar nodo inexistente con camino ausente; validación HTTP 400; `INTERNAL_ERROR` como quinto estado de forwarding, diferenciado del error HTTP 500.

**Prompt real / salida / corrección / responsable:** [completar con evidencia real].

### P5 — Plan de implementación y trazabilidad

**Prompt de referencia:** Divide el trabajo entre Controller y Router, identifica dependencias y entregables por tarea, vincula FR/NFR con componentes y pruebas. No asignes pruebas a funcionalidades que no existan en la especificación.

**Crítica/decisiones que debe confirmar el equipo:** integración conjunta, contratos cerrados antes de implementar y tareas de ambos miembros visibles.

**Prompt real / salida / corrección / responsable:** [completar con evidencia real].

### P6 — Revisión de pruebas y ambigüedades

**Prompt de referencia:** Actúa como revisor de calidad. Identifica al menos tres ambigüedades entre requisitos, arquitectura, API y pruebas; propone alternativas, sin elegir silenciosamente por el equipo. Para cada decisión, enumera documentos afectados y pruebas necesarias.

**Crítica/decisiones que debe confirmar el equipo:** registrar las decisiones aceptadas en los documentos y mantener el mapeo entre los casos TC-01..TC-09 del taller y los casos detallados TX.

**Prompt real / salida / corrección / responsable:** [completar con evidencia real].

## Registro consolidado de evidencia

| Técnica | Prompt real usado | Salida relevante | Ambigüedad encontrada | Decisión humana | Documentos afectados |
|---|---|---|---|---|---|
| Contextual framing | [completar] | [completar] | [completar] | [completar] | 01–06 |
| Structured prompting | [completar] | [completar] | [completar] | [completar] | 01, 04, 06 |
| Role prompting | [completar] | [completar] | [completar] | [completar] | 02, 03, 05 |
| Few-shot | [completar] | [completar] | [completar] | [completar] | 04, 06 |
| Iterative refinement | [completar] | [completar] | [completar] | [completar] | 01–06 |
