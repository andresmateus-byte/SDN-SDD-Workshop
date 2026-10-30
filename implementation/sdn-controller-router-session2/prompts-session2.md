# Registro de ingeniería de prompts — Sesión 2

**Propósito:** documentar prompts de implementación, pruebas y revisión crítica exigidos por el taller. Esta versión es una base de trabajo construida a partir de la estructura del repositorio; el equipo debe pegar o ajustar los prompts realmente utilizados y completar la evidencia de ejecución. No atribuir al equipo salidas o pruebas que no haya observado.

## Prompt 1 — Generación del Controller desde la especificación

- **Técnica:** contextual framing + restricciones estructuradas.
- **Objetivo:** implementar carga JSON, MVC/DAO, rutas Dijkstra y endpoints sin mezclar lógica de negocio con HTTP.
- **Prompt base:**

> Actúa como ingeniero Python senior. Implementa el SDN Controller siguiendo `specs/01-requirements.md`, `specs/02-static-architecture.md` y `specs/04-api-contract.md` como fuente de verdad. Usa Python 3.11+, FastAPI, NetworkX, MVC, DAO e inyección de dependencias. El DAO debe validar la topología JSON y mantener fallas/restauraciones en memoria. RoutingService debe usar Dijkstra y las métricas delay, bandwidth (suma de 1/b) y loss (-ln(1-p)); los enlaces con p=1 no pueden usarse. Mantén los endpoints como coordinadores del servicio, normaliza validación a HTTP 400 INVALID_INPUT y entrega módulos y pruebas separados. No inventes endpoints ni campos JSON.

- **Salida relevante a verificar:** módulos `controller/domain`, `controller/dao`, `controller/services` y `controller/controllers`.
- **Crítica aplicada:** la respuesta debe verificarse contra el contrato, en especial 400 en vez de 422, `NODE_NOT_FOUND` frente a `PATH_NOT_FOUND`, versión de topología e idempotencia.
- **Evidencia del equipo:** [pegar respuesta/prompts reales y commit asociado].
- **Requisitos relacionados:** FR-01 a FR-06; NFR-01 a NFR-09.

## Prompt 2 — Implementación de métricas (few-shot)

- **Técnica:** few-shot con ejemplos de entrada/salida.
- **Objetivo:** impedir que la métrica bandwidth se confunda con máximo ancho de banda de cuello de botella.
- **Prompt base:**

> Implementa las tres estrategias de costo con estas reglas exactas: delay=d; bandwidth=1/b para b>0; loss=-ln(1-p) para 0≤p<1. Si p=1, excluye el enlace del grafo aunque esté activo. Ejemplos: dos enlaces de 100 Mbps dan costo bandwidth 0.02; dos enlaces con pérdida 0.01 dan costo loss -ln(0.99)*2. Todos los pesos usados por Dijkstra deben ser no negativos. Separa las estrategias del endpoint y añade tests con tolerancia numérica.

- **Salida relevante a verificar:** estrategias independientes y pruebas numéricas.
- **Crítica aplicada:** verificar fórmulas con cálculo manual; no describir `1/b` como maximización de ancho de banda.
- **Evidencia del equipo:** [pegar salida real y resultado del test].
- **Requisitos relacionados:** FR-03, FR-04; TX de métricas en `specs/06-test-specification.md`.

## Prompt 3 — Implementación del Router sin enrutamiento local

- **Técnica:** role prompting + restricciones negativas explícitas.
- **Objetivo:** asegurar que el Router solo solicita la ruta al Controller y simula los saltos.
- **Prompt base:**

> Actúa como responsable de la aplicación Router. Implementa Packet, ForwardingResult, ControllerClient/HttpControllerClient, ForwardingService, ForwardingLogDAO/FileForwardingLogDAO y endpoints FastAPI. El Router nunca debe importar NetworkX ni calcular rutas. Para cada paquete localmente válido, hace una sola consulta GET /route, valida la respuesta, simula `trace=path` y persiste el resultado JSONL. Usa timeout configurable sin reintentos. Traduce transporte/timeout/respuesta inválida a 503 CONTROLLER_UNAVAILABLE; conserva NODE_NOT_FOUND y PATH_NOT_FOUND del Controller. Si falla la persistencia, responde 500 sin afirmar que se guardó.

- **Salida relevante a verificar:** cliente inyectable, servicio sin dependencia HTTP concreta y DAO reemplazable.
- **Crítica aplicada:** revisar que los errores posteriores a validación lleven `packet_id`, y que un 400 local no genere registro.
- **Evidencia del equipo:** [pegar salida real y revisión].
- **Requisitos relacionados:** FR-07 a FR-10; NFR-01, NFR-02, NFR-06, NFR-07 y NFR-09.

## Prompt 4 — Revisión de contrato mediante casos concretos

- **Técnica:** structured prompting + ejemplos de borde.
- **Objetivo:** contrastar las respuestas reales con el contrato API.
- **Prompt base:**

> Revisa los endpoints contra `specs/04-api-contract.md`. Para cada caso enumera request, status HTTP, código de error, campos obligatorios y efecto en el DAO: (1) campo src ausente; (2) nodo inexistente; (3) nodos existentes sin camino; (4) Controller caído; (5) métrica inválida; (6) escritura JSONL fallida. No cambies la especificación para que coincida con una implementación incorrecta. Sugiere tests automatizados reproducibles.

- **Salida relevante a verificar:** matriz de contrato y tests de error.
- **Crítica aplicada:** no confundir error de validación 400, ausencia de nodo 404 y camino ausente 404; diferenciar el estado persistido `INTERNAL_ERROR` del error HTTP 500.
- **Evidencia del equipo:** [pegar tabla y pruebas].
- **Requisitos relacionados:** FR-05, FR-09, FR-10; NFR-04 y NFR-06.

## Prompt 5 — Dobles de prueba y aislamiento arquitectónico

- **Técnica:** iterative refinement.
- **Objetivo:** demostrar que RoutingService y ForwardingService pueden probarse sin levantar servidores HTTP.
- **Prompt base:**

> Crea FakeTopologyDAO, FakeControllerClient e InMemoryForwardingLogDAO. Añade tests que inyecten esos dobles directamente en RoutingService y ForwardingService, sin abrir puertos ni depender de archivos reales. Comprueba llamadas, estados persistidos, fallos de cliente y fallos de persistencia. Mantén el test determinista y explica qué requisito arquitectónico demuestra cada prueba.

- **Salida relevante a verificar:** `TC-08`/`TC-09` cubiertos por tests de servicio.
- **Crítica aplicada:** comprobar que el test no construye TestClient ni levanta Uvicorn para demostrar aislamiento de servicio.
- **Evidencia del equipo:** [pegar salida real y nombres de tests].
- **Requisitos relacionados:** NFR-02, NFR-07 y NFR-09.

## Prompt 6 — Revisión adversarial del repositorio

- **Técnica:** rol de revisor crítico + refinamiento iterativo.
- **Objetivo:** encontrar defectos antes de la integración.
- **Prompt base:**

> Revisa este repositorio como evaluador estricto del taller. No asumas que compila ni que pasa los tests. Busca: imports incorrectos, errores FastAPI que devuelven 422, rutas no coincidentes con el contrato, algoritmo en controladores, acceso a archivos desde servicios, Router que calcule rutas, errores que maten el proceso, errores de persistencia mal clasificados, pruebas que dependan de servicios externos y ausencia de trazabilidad. Devuelve defectos priorizados, evidencia por archivo y correcciones concretas; no inventes resultados de ejecución.

- **Salida relevante a verificar:** lista de defectos y correcciones vinculadas a commits.
- **Crítica aplicada:** cada observación debe verificarse contra código y ejecutarse en test; una sugerencia de IA no constituye evidencia de que la corrección funciona.
- **Evidencia del equipo:** [pegar hallazgos confirmados, correcciones y commits].
- **Requisitos relacionados:** NFR-01 a NFR-09; pruebas de arquitectura.

## Registro de ejecución real

| Fecha/hora | Prompt | Archivo/commit afectado | Resultado observado | Corrección realizada | Verificado por |
|---|---|---|---|---|---|
| [completar] | P1 | [completar] | [completar] | [completar] | [A/B] |
| [completar] | P2 | [completar] | [completar] | [completar] | [A/B] |
| [completar] | P3 | [completar] | [completar] | [completar] | [A/B] |
| [completar] | P4 | [completar] | [completar] | [completar] | [A/B] |
| [completar] | P5 | [completar] | [completar] | [completar] | [A/B] |
| [completar] | P6 | [completar] | [completar] | [completar] | [A/B] |
