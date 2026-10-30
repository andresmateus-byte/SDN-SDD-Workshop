# 06 — Especificación de pruebas

## Sistema educativo tipo SDN: Controller y Router

| Campo | Detalle |
| :---- | :---- |
| Proyecto | Aplicaciones Controller y Router comunicadas por REST/JSON |
| Documento | `specs/06-test-specification.md` |
| Versión | 1.2 — línea base aprobada |
| Fecha | 27 de octubre de 2026 |
| Estado | Especificación aprobada; las pruebas no se han declarado ejecutadas |
| Documentos base | `01-requirements.md` v1.2, `02-static-architecture.md` v1.2, `03-dynamic-architecture.md` v1.2, `04-api-contract.md` v1.2 y `05-implementation-plan.md` v1.1 |
| Responsable Controller | Andrés Felipe Mateus |
| Responsable Router | Santiago Cavarro |
| Aprobación | Aprobado, 27 de octubre de 2026 — ambos integrantes |

---

## 1\. Propósito

Este documento formaliza la estrategia, los casos de prueba, los criterios de aceptación y la trazabilidad necesarios para verificar la solución simulada tipo SDN formada por dos procesos independientes: **Controller** y **Router**. Convierte los requisitos FR/NFR, los contratos HTTP/JSON, los escenarios dinámicos y las tareas de implementación en comprobaciones reproducibles.

Los identificadores `TC-xx` de este documento son los identificadores de pruebas. Los identificadores `CT-xx` de `04-api-contract.md` son comprobaciones de contrato y **no son intercambiables** con los `TC-xx`. Una prueba definida no equivale a una prueba ejecutada ni aprobada: los resultados reales deberán registrarse al ejecutar la implementación.

## 2\. Alcance de verificación

### 2.1 Incluido

- Carga y validación de topología JSON, estado inicial y versionado.  
- Cálculo de rutas mínimas con Dijkstra y métricas `delay`, `bandwidth` y `loss`.  
- API REST del Controller y del Router, incluidos esquemas, estados HTTP y códigos de aplicación.  
- Falla/restauración de enlaces, idempotencia, actualización de rutas y consistencia de versión.  
- Solicitud HTTP del Router al Controller, validación de la respuesta y simulación de saltos.  
- Registro mediante DAO de resultados de reenvío, así como el comportamiento ante fallos de persistencia.  
- Manejo de entradas inválidas, errores de aplicación, transporte, timeout y respuestas incompatibles.  
- Separación arquitectónica, inyección de dependencias, configuración, continuidad del proceso, rendimiento y resiliencia.

### 2.2 Excluido

No se verifican OpenFlow, tráfico real de red, interfaz gráfica, autenticación, autorización, persistencia de estado operativo de enlaces entre reinicios, ni descartes aleatorios de paquetes. La pérdida solo interviene en el costo de enrutamiento. No se mide rendimiento de producción ni se establece un límite funcional de tamaño de topología.

## 3\. Referencias y reglas de precedencia

1. **Entregable 01:** fuente de requisitos FR/NFR, reglas de validación de topología y criterios de aceptación.  
2. **Entregable 02:** fuente de componentes, capas, interfaces y dependencias arquitectónicas.  
3. **Entregable 03:** fuente de secuencias, variantes, invariantes y comportamiento temporal.  
4. **Entregable 04:** contrato normativo de endpoints, campos, esquemas, códigos HTTP y errores.  
5. **Entregable 05:** fuente de fases, configuración aprobada, tareas `IMP-xx` y evidencia prevista.

Si una prueba contradice el contrato aprobado, no se debe modificar la expectativa solo para que pase la implementación. Se debe abrir una incidencia y aplicar el control de cambios. La línea base documental está aprobada; las discrepancias que aparezcan durante la ejecución se registran como incidencias y se gestionan mediante el control de cambios.

## 4\. Estrategia de pruebas

| Nivel | Objetivo | Entorno y dobles permitidos | Evidencia mínima |
| :---- | :---- | :---- | :---- |
| Unitario de dominio | Validar reglas de nodos, enlaces, métricas, rutas, estados y versionado. | Datos en memoria; sin red ni archivos reales. | Resultado de cada `TC` y aserciones de valores. |
| Unitario de servicios | Verificar `RoutingService` y `ForwardingService`, incluidas ramas de error. | `FakeTopologyDAO`, `FakeControllerClient`, `InMemoryForwardingLogDAO`, reloj falso y mocks. | Pruebas deterministas y verificación de llamadas. |
| DAO | Validar archivos, serialización, lectura, escritura y errores de E/S. | Archivos temporales aislados. | Contenido antes/después y excepciones observadas. |
| Contrato API | Comprobar método, ruta, HTTP, esquema y código de aplicación. | Cliente ASGI o aplicaciones de prueba. | Solicitud, respuesta y validaciones del esquema. |
| Integración | Validar comunicación entre procesos reales y efectos observables. | Controller y Router independientes; puertos y archivos temporales. | Comandos, respuestas, registros y logs sanitizados. |
| Arquitectura | Verificar MVC, DAO, inyección y ubicación de la lógica. | Inspección de dependencias, análisis estático y revisión de código. | Lista de controles con evidencia y resultado. |
| Rendimiento | Medir latencia HTTP completa de `GET /route`. | Controller y cliente en la misma máquina; topología sintética reproducible. | Muestras, p95, entorno y parámetros. |
| Resiliencia | Verificar fallo del Controller, timeout, recuperación y salud del Router. | Procesos controlados por la prueba. | Latencia, HTTP/código de error y respuesta posterior de salud. |

### 4.1 Convenciones de resultado

- **APROBADA:** todas las condiciones observables de la prueba se cumplen.  
- **FALLIDA:** al menos una condición verificable no se cumple.  
- **BLOQUEADA:** no puede ejecutarse por falta de una decisión aprobada, entorno o implementación.  
- **NO EJECUTADA:** existe el caso, pero todavía no se ha intentado ejecutar.

En esta versión todos los casos están **NO EJECUTADOS**. No se debe convertir una expectativa documentada en evidencia de cumplimiento.

### 4.2 Severidad sugerida para incidencias

- **Crítica:** impide arrancar o rompe el contrato esencial, produce resultados incorrectos de enrutamiento o contradice la separación Controller/Router.  
- **Alta:** clasifica mal un error, pierde consistencia de versión, registra un estado inválido o deja inoperativa una aplicación ante un error esperado.  
- **Media:** falla una configuración alternativa, un esquema secundario o una condición de borde sin afectar el flujo principal.  
- **Baja:** defecto de mensaje o documentación que no altera código HTTP, código de aplicación ni estado del sistema.

## 5\. Entorno y datos de prueba

### 5.1 Entorno de referencia

- Python 3.11 o superior.  
- FastAPI, Uvicorn, NetworkX, `pytest` y cliente HTTP con timeout configurable, según `05-implementation-plan.md`.  
- Controller y Router como procesos separados, sin estado de dominio compartido.  
- Puertos predeterminados aprobados: Controller `8001`, Router `8002`.  
- Topología predeterminada aprobada: `data/topology.json`.  
- Registro de resultados aprobado: `logs/forwarding.jsonl`.  
- Timeout predeterminado del cliente Router→Controller: 2 segundos y un único intento sin reintentos automáticos.
- La configuración se lee desde variables de entorno con nombres correspondientes a las claves de 05 en mayúsculas.

Las pruebas no deben depender de esos puertos o rutas fijas: deben aceptar configuración alternativa para comprobar NFR-05 y evitar conflictos con otros procesos.

### 5.2 Topología de referencia T1

Usar los siguientes enlaces no dirigidos. Todos comienzan activos, `topology_version = 1`.

| Enlace | `delay_ms` | `bandwidth_mbps` | `loss_probability` |
| :---- | ----: | ----: | ----: |
| A–B | 10 | 100 | 0.01 |
| B–D | 10 | 100 | 0.01 |
| A–C | 15 | 50 | 0.02 |
| C–D | 20 | 50 | 0.02 |

Expectativas de referencia para A→D:

- Con `delay`: ruta única mínima `A-B-D`, costo `20`.  
- Con `bandwidth`: costo de `A-B-D` igual a `1/100 + 1/100 = 0.02`.  
- Con `loss`: costo de `A-B-D` igual a `-ln(0.99) × 2`; `exp(-total_cost)` debe coincidir con `0.99 × 0.99` dentro de tolerancia `1e-9`.  
- Tras fallar B–D, ruta alternativa `A-C-D`, costo de retardo `35`, versión `2`.  
- Tras fallar además C–D, no hay ruta A→D; versión `3`.  
- Tras restaurar B–D, la ruta mínima A–B–D vuelve a estar disponible; versión `4`.

Esta topología es adecuada para la secuencia de demostración de 04\. Las pruebas de caminos con empate deben aceptar cualquier camino de costo mínimo, conforme a A-09.

### 5.3 Topologías auxiliares

- **T2 — lineal:** A–B–C, para comprobar una topología distinta sin modificar el código.  
- **T3 — desconectada:** A–B y C–D, para diferenciar `NODE_NOT_FOUND` de `PATH_NOT_FOUND`.  
- **T4 — enlace con pérdida total:** una topología que incluya un enlace con `loss_probability = 1` y una ruta alternativa, para comprobar que ese enlace nunca se usa, aunque figure `active = true`.  
- **T5 — rendimiento:** grafo sintético conectado de al menos 50 nodos y 150 enlaces; los parámetros y el generador deben versionarse o guardarse para reproducibilidad.  
- **T6 — carga inválida:** variantes aisladas de T1 para cada condición inválida, no una única entrada con múltiples errores.

### 5.4 Dobles de prueba requeridos

- `FakeTopologyDAO`: devuelve instantáneas controladas y permite observar las llamadas al DAO.  
- `FakeControllerClient`: permite devolver una ruta válida, errores de aplicación, timeout, error de transporte, respuesta malformada o incompatible.  
- `InMemoryForwardingLogDAO`: registra resultados en memoria y permite inspeccionarlos.  
- `FailingForwardingLogDAO`: falla de manera determinista en `save()`.  
- Reloj inyectable/falso para verificar timestamp sin depender del reloj real.

Los servicios deben recibir estos objetos por inyección; las pruebas unitarias no deben iniciar servidores reales ni tocar archivos de usuario.

## 5.5 Casos de aceptación del taller (IDs TC-01 a TC-09)

Los identificadores `TC-01` a `TC-09` conservan el significado fijado por el PDF del taller. No se reutilizan para los casos detallados de este documento, que se identifican como `TX-01` a `TX-69`. Cada TC del taller se implementa mediante los casos TX indicados en esta tabla.

| ID del PDF | Significado fijo | Casos detallados que lo implementan |
| :---- | :---- | :---- |
| TC-01 | Dijkstra elige el camino mínimo esperado. | TX-09–TX-12 y TX-31 |
| TC-02 | Métricas `delay`, `bandwidth` y `loss`. | TX-13–TX-17 |
| TC-03 | Los enlaces fallados se excluyen del cálculo. | TX-25, TX-29, TX-31 y TX-63–TX-64 |
| TC-04 | Restaurar un enlace actualiza las rutas. | TX-27–TX-28, TX-31 y TX-65 |
| TC-05 | El Router obtiene la ruta por HTTP. | TX-39, TX-43–TX-49 y TX-62–TX-67 |
| TC-06 | La traza reporta un resultado válido. | TX-37–TX-38 y TX-62–TX-65 |
| TC-07 | Caída del Controller o destino inalcanzable. | TX-10, TX-24, TX-45–TX-49, TX-57–TX-58 y TX-64, TX-66–TX-67 |
| TC-08 | `RoutingService` con `TopologyDAO` falso, sin servidor HTTP. | TX-34 |
| TC-09 | `ForwardingService` con su DAO de registro, de forma independiente del servidor HTTP. | TX-50–TX-55 (en particular TX-52) |

### Tabla de equivalencia de los IDs detallados anteriores

Los antiguos IDs `TC-01` a `TC-68` de las tablas detalladas se renombraron `TX-01` a `TX-68`, conservando su contenido. La columna final indica el TC del PDF que ofrece la cobertura funcional más próxima; “Complementario” señala comprobaciones adicionales que no sustituyen ni alteran el significado fijo de TC-01 a TC-09.

| ID anterior en 06 v1.0 | ID detallado vigente | TC del PDF que cubre |
| :---- | :---- | :---- |
| TC-01 (ID anterior) | TX-01 | TC-08 (carga/DAO relacionada) |
| TC-02 (ID anterior) | TX-02 | TC-08 (carga/DAO relacionada) |
| TC-03 (ID anterior) | TX-03 | TC-08 (carga/DAO relacionada) |
| TC-04 (ID anterior) | TX-04 | TC-08 (carga/DAO relacionada) |
| TC-05 (ID anterior) | TX-05 | TC-08 (carga/DAO relacionada) |
| TC-06 (ID anterior) | TX-06 | TC-08 (carga/DAO relacionada) |
| TC-07 (ID anterior) | TX-07 | TC-08 (carga/DAO relacionada) |
| TC-08 (ID anterior) | TX-08 | TC-08 (carga/DAO relacionada) |
| TC-09 (ID anterior) | TX-09 | TC-01 |
| TC-10 (ID anterior) | TX-10 | TC-01 |
| TC-11 (ID anterior) | TX-11 | TC-01 |
| TC-12 (ID anterior) | TX-12 | TC-01 |
| TC-13 (ID anterior) | TX-13 | TC-02 |
| TC-14 (ID anterior) | TX-14 | TC-02 |
| TC-15 (ID anterior) | TX-15 | TC-02 |
| TC-16 (ID anterior) | TX-16 | TC-02 |
| TC-17 (ID anterior) | TX-17 | TC-02 |
| TC-18 (ID anterior) | TX-18 | Complementario (contrato Controller) |
| TC-19 (ID anterior) | TX-19 | Complementario (contrato Controller) |
| TC-20 (ID anterior) | TX-20 | Complementario (contrato Controller) |
| TC-21 (ID anterior) | TX-21 | TC-01 / TC-07 (ruta y destinos) |
| TC-22 (ID anterior) | TX-22 | TC-01 / TC-07 (ruta y destinos) |
| TC-23 (ID anterior) | TX-23 | TC-01 / TC-07 (ruta y destinos) |
| TC-24 (ID anterior) | TX-24 | TC-01 / TC-07 (ruta y destinos) |
| TC-25 (ID anterior) | TX-25 | TC-03 / TC-04 |
| TC-26 (ID anterior) | TX-26 | TC-03 / TC-04 |
| TC-27 (ID anterior) | TX-27 | TC-04 |
| TC-28 (ID anterior) | TX-28 | TC-04 |
| TC-29 (ID anterior) | TX-29 | TC-03 / TC-04 |
| TC-30 (ID anterior) | TX-30 | Complementario (validación de contrato) |
| TC-31 (ID anterior) | TX-31 | TC-03 / TC-04 |
| TC-32 (ID anterior) | TX-32 | TC-03 / TC-04 |
| TC-33 (ID anterior) | TX-33 | TC-03 / TC-04 |
| TC-34 (ID anterior) | TX-34 | TC-08 |
| TC-35 (ID anterior) | TX-35 | Complementario (error interno Controller) |
| TC-36 (ID anterior) | TX-36 | Complementario (configuración) |
| TC-37 (ID anterior) | TX-37 | TC-06 |
| TC-38 (ID anterior) | TX-38 | TC-06 |
| TC-39 (ID anterior) | TX-39 | TC-05 |
| TC-40 (ID anterior) | TX-40 | TC-05 |
| TC-41 (ID anterior) | TX-41 | Complementario (validación Router) |
| TC-42 (ID anterior) | TX-42 | Complementario (validación Router) |
| TC-43 (ID anterior) | TX-43 | TC-05 (consulta HTTP) / complementario (nodo inválido) |
| TC-44 (ID anterior) | TX-44 | TC-07 |
| TC-45 (ID anterior) | TX-45 | TC-05 / TC-07 |
| TC-46 (ID anterior) | TX-46 | TC-05 / TC-07 |
| TC-47 (ID anterior) | TX-47 | TC-05 / TC-07 |
| TC-48 (ID anterior) | TX-48 | TC-05 / TC-07 |
| TC-49 (ID anterior) | TX-49 | TC-05 / TC-07 |
| TC-50 (ID anterior) | TX-50 | TC-09 |
| TC-51 (ID anterior) | TX-51 | TC-09 |
| TC-52 (ID anterior) | TX-52 | TC-09 |
| TC-53 (ID anterior) | TX-53 | TC-09 |
| TC-54 (ID anterior) | TX-54 | TC-09 |
| TC-55 (ID anterior) | TX-55 | TC-09 |
| TC-56 (ID anterior) | TX-56 | Complementario (salud Router) |
| TC-57 (ID anterior) | TX-57 | TC-07 |
| TC-58 (ID anterior) | TX-58 | TC-05 |
| TC-59 (ID anterior) | TX-59 | Complementario (configuración) |
| TC-60 (ID anterior) | TX-60 | TC-09 (arquitectura relacionada) |
| TC-61 (ID anterior) | TX-61 | Complementario (salud de procesos) |
| TC-62 (ID anterior) | TX-62 | TC-05 / TC-06 |
| TC-63 (ID anterior) | TX-63 | TC-03 / TC-05 / TC-07 |
| TC-64 (ID anterior) | TX-64 | TC-03 / TC-05 / TC-07 |
| TC-65 (ID anterior) | TX-65 | TC-04 / TC-05 / TC-06 |
| TC-66 (ID anterior) | TX-66 | TC-07 |
| TC-67 (ID anterior) | TX-67 | TC-07 |
| TC-68 (ID anterior) | TX-68 | Complementario (entrada inválida) |
| Nuevo (sin ID anterior) | TX-69 | Complementario (excepción interna inesperada; CT-37) |

## 6. Casos de prueba del Controller

Todos los casos de esta sección tienen como responsable principal a **Andrés Felipe Mateus**. El resultado real se registra después de la ejecución.

| ID | Tipo | Requisitos / CT | Preparación y acción | Resultado esperado |
| :---- | :---- | :---- | :---- | :---- |
| TX-01 | Unitario/DAO | FR-01, AC-01.1, CT-02 | Cargar T1 desde JSON válido. | Se cargan exactamente los nodos y enlaces definidos; todos activos; versión inicial `1`. |
| TX-02 | DAO/integración | FR-01, NFR-06 | Arrancar con archivo inexistente. | El Controller no inicia; termina con código distinto de cero y mensaje descriptivo. |
| TX-03 | DAO | FR-01, NFR-06 | Cargar JSON sintácticamente mal formado. | Se rechaza la carga y el Controller no inicia. |
| TX-04 | DAO | FR-01 | Probar por separado nodo vacío, solo espacios y nodo duplicado. | Cada entrada se rechaza con error descriptivo; no se crea topología parcialmente válida. |
| TX-05 | DAO | FR-01 | Probar enlace con nodo inexistente, extremos iguales y enlace duplicado en el mismo orden. | Se rechaza cada topología inválida. |
| TX-06 | DAO | FR-01 | Probar enlace duplicado con extremos invertidos. | Se rechaza como duplicado; la topología trata los enlaces como no dirigidos. |
| TX-07 | DAO | FR-01 | Probar por separado `delay_ms < 0`, `bandwidth_mbps <= 0`, `loss_probability < 0` y `loss_probability > 1`. | Cada valor inválido impide el inicio y el mensaje identifica el campo/enlace afectado. |
| TX-08 | Unitario/DAO | FR-01, A-02 | Cargar enlace con `delay_ms=0`, `loss_probability=0` y otro con `loss_probability=1`. | Los límites permitidos se aceptan; `p=1` no se elimina del modelo, pero no es elegible para ninguna ruta. |
| TX-09 | Unitario | FR-02, AC-02.1 | Calcular rutas en T1 y T2 sin modificar código. | Las dos topologías válidas se procesan correctamente; no existe lógica codificada para una sola topología. |
| TX-10 | Unitario | FR-02, FR-03, CT-11 | Consultar ruta entre componentes distintos de T3. | `PATH_NOT_FOUND`; no se confunde con un nodo inexistente. |
| TX-11 | Unitario | FR-03, AC-03.1, CT-03 | Consultar A→D en T1 con `delay`. | Ruta `A-B-D`, costo `20`, métrica `delay`, versión `1`. |
| TX-12 | Unitario | FR-03, AC-03.2, CT-07 | Consultar A→A. | Ruta `[A]`, costo `0`, versión actual. |
| TX-13 | Unitario | FR-04, AC-04.1, CT-03 | Calcular ruta con `delay`. | El costo total equivale a la suma de `delay_ms` de los enlaces de la ruta. |
| TX-14 | Unitario | FR-04, AC-04.2, CT-04 | Calcular ruta con `bandwidth`. | El costo equivale a la suma de `1/bandwidth_mbps` por enlace. |
| TX-15 | Unitario | FR-04, AC-04.3, CT-05 | Calcular ruta con `loss`. | `exp(-total_cost)` coincide con el producto de `(1-p)` de los enlaces, tolerancia absoluta `1e-9`. |
| TX-16 | Unitario | FR-04, AC-04.4 | Consultar ruta en T4. | Ninguna ruta incluye el enlace con `loss_probability=1`, incluso si está activo. |
| TX-17 | Unitario | FR-04, AC-04.5 | Comparar rutas entre métricas en una topología diseñada para producir caminos distintos. | Al menos un par origen-destino produce caminos mínimos diferentes según la métrica. |
| TX-18 | Contrato | FR-05, CT-01 | Solicitar `GET /health` del Controller. | HTTP `200`; JSON `status="ok"`, `application="controller"`. |
| TX-19 | Contrato | FR-05, CT-02, CT-27 | Solicitar `GET /topology`. | HTTP `200`; campos, tipos y nombres según 04; enlaces con `active`; versión entera `>=1`. |
| TX-20 | Contrato | FR-05, CT-06 | Consultar `GET /route` omitiendo `metric`. | HTTP `200`; la métrica devuelta es `delay`. |
| TX-21 | Contrato | FR-05, FR-09, CT-08 | Consultar `/route` sin `src` o sin `dst`, con valor vacío o solo espacios. | HTTP `400`, `error="INVALID_INPUT"`; nunca `422`. |
| TX-22 | Contrato | FR-04, FR-09, CT-09 | Consultar `/route?metric=speed`. | HTTP `400`, `INVALID_INPUT`; el mensaje es informativo y no se usa como clave de lógica. |
| TX-23 | Contrato | FR-03, FR-09, CT-10 | Consultar ruta con origen o destino inexistente. | HTTP `404`, `NODE_NOT_FOUND`; cuerpo `ErrorResponse` conforme a 04\. |
| TX-24 | Contrato | FR-03, FR-09, CT-11 | Consultar ruta entre nodos existentes sin camino. | HTTP `404`, `PATH_NOT_FOUND`, distinto de `NODE_NOT_FOUND`. |
| TX-25 | Contrato/DAO | FR-06, CT-12 | Fallar un enlace activo con `POST /links/fail`. | HTTP `200`; `active=false`, `changed=true`; versión incrementada exactamente en uno. |
| TX-26 | Contrato | FR-06, CT-13 | Repetir la falla sobre el mismo enlace ya fallado. | HTTP `200`; `changed=false`; versión sin cambios. |
| TX-27 | Contrato | FR-06, CT-16 | Restaurar enlace fallado. | HTTP `200`; `active=true`, `changed=true`; versión incrementada exactamente en uno. |
| TX-28 | Contrato | FR-06, CT-28 | Restaurar un enlace que ya está activo. | HTTP `200`; `changed=false`; versión sin cambios. |
| TX-29 | Contrato | FR-06, CT-14, CT-17, CT-35 | Fallar/restaurar enlace inexistente, con extremos iguales o nodos no enlazados. | HTTP `404`, `LINK_NOT_FOUND`; la topología y la versión no cambian. |
| TX-30 | Contrato | FR-06, CT-15, CT-29 | Enviar cuerpo ausente, JSON inválido o extremos ausentes/no textuales a operaciones de enlace. | HTTP `400`, `INVALID_INPUT`; no cambia el estado ni la versión. |
| TX-31 | Integración | FR-06, AC-06.1, AC-06.2 | En T1, fallar B–D, consultar A→D y después restaurar B–D. | La ruta nueva evita el enlace fallado; tras restaurar, B–D vuelve a ser elegible. Si hay empate mínimo, se acepta cualquier ruta mínima. |
| TX-32 | DAO/integración | FR-06, AC-06.5, A-05 | Guardar hash/contenido del JSON; fallar y restaurar enlaces; comparar archivo. | El archivo de topología no se modifica; el estado operativo solo vive en memoria. |
| TX-33 | Integración | FR-01, A-05 | Cambiar el estado de un enlace y reiniciar Controller con el mismo archivo. | Todos los enlaces vuelven a activos y la versión vuelve a `1`. |
| TX-34 | Arquitectura | NFR-01, NFR-02, NFR-03, NFR-07, NFR-09 | Inspeccionar dependencias y probar `RoutingService` con `FakeTopologyDAO`. | El servicio depende de la interfaz DAO; no accede directamente a archivos ni contiene lógica HTTP; Dijkstra está en `RoutingService`. |
| TX-35 | Contrato/error interno | FR-05, FR-09, CT-33, CT-34 | Provocar un error interno determinista en cada endpoint afectado (`/route` y `/topology`; `/health` si procede). | HTTP `500`, `INTERNAL_ERROR`; JSON según 04; no se exponen trazas ni detalles internos; el proceso continúa activo. |
| TX-36 | Configuración | NFR-05 | Arrancar Controller con puerto alternativo y ruta de topología alternativa válida. | Arranca y responde por la configuración alternativa sin cambiar código fuente. |

## 7. Casos de prueba del Router

Responsable principal: **Santiago Cavarro**.

| ID | Tipo | Requisitos / CT | Preparación y acción | Resultado esperado |
| :---- | :---- | :---- | :---- | :---- |
| TX-37 | Unitario/contrato | FR-08, CT-18, CT-19 | Enviar paquete válido A→D y simular respuesta de ruta válida. | HTTP `200`; `status="DELIVERED"`; `trace` coincide exactamente con `path`; campos y tipos de 04\. |
| TX-38 | Unitario | FR-08, CT-20 | Enviar paquete válido sin `packet_id`. | Se genera un ID no vacío, se devuelve y se usa en el resultado persistido. |
| TX-39 | Unitario | FR-07, FR-08, AC-07.1 | Enviar paquete válido con `FakeControllerClient` que cuente llamadas. | Se hace exactamente una solicitud lógica de ruta por paquete; no hay reintentos automáticos. |
| TX-40 | Unitario | FR-07, FR-08, AC-07.2 | Inspeccionar dependencias/importaciones y ejecutar un reenvío. | Router no importa NetworkX ni implementa Dijkstra; usa la ruta recibida del Controller sin recalcularla. |
| TX-41 | Contrato | FR-08, FR-09, CT-21, CT-30 | Enviar JSON inválido, campos requeridos ausentes, `src`/`dst` vacíos o solo espacios. | HTTP `400`, `INVALID_INPUT`; sin llamada al Controller, sin intento de persistencia y sin `packet_id` en el cuerpo de error. |
| TX-42 | Contrato | FR-09, CT-22, CT-36 | Enviar métrica no soportada, `packet_id` vacío, solo espacios o de más de 64 caracteres. | HTTP `400`, `INVALID_INPUT`; no se consulta Controller ni se registra el paquete. |
| TX-43 | Integración | FR-09, FR-10, CT-23 | Controller devuelve `404 NODE_NOT_FOUND` válido. | Router devuelve HTTP `404`, conserva `NODE_NOT_FOUND`, incluye `packet_id` y persiste `INVALID_NODE` si el DAO funciona. |
| TX-44 | Integración | FR-09, FR-10, CT-24 | Controller devuelve `404 PATH_NOT_FOUND` válido. | Router devuelve HTTP `404`, conserva `PATH_NOT_FOUND`, incluye `packet_id` y persiste `NO_ROUTE` si el DAO funciona. |
| TX-45 | Unitario/integración | FR-09, FR-10, CT-25 | Controller rechaza conexión o está detenido. | Router devuelve `503`, `CONTROLLER_UNAVAILABLE`, incluye `packet_id` y persiste el estado homónimo si el DAO funciona. |
| TX-46 | Unitario | FR-09, FR-10 | El cliente HTTP agota el timeout configurado. | Una sola llamada; `503 CONTROLLER_UNAVAILABLE`; se intenta registrar el estado correspondiente si el DAO funciona. |
| TX-47 | Unitario | FR-09, FR-10, CT-26, CT-32 | Simular respuesta 200 con JSON malformado, campos obligatorios ausentes o tipos incompatibles. | `503 CONTROLLER_UNAVAILABLE`; no se calcula ruta local; se intenta persistir el estado correspondiente. |
| TX-48 | Unitario | FR-09, FR-10, CT-32 | Simular respuesta 5xx, 400 inesperado, 404 con código desconocido o respuesta incompatible. | `503 CONTROLLER_UNAVAILABLE`; se intenta registrar ese estado si la persistencia funciona. |
| TX-49 | Unitario | FR-09, FR-10 | Simular error de transporte distinto de timeout (por ejemplo, conexión interrumpida). | `503 CONTROLLER_UNAVAILABLE`; proceso Router continúa activo. |
| TX-50 | Unitario | FR-10, AC-10.1 | Ejecutar reenvío exitoso con `InMemoryForwardingLogDAO`. | Un registro con `packet_id`, `status=DELIVERED`, `src`, `dst`, `path`, `trace`, métrica, costo, versión y timestamp conforme al contrato interno. |
| TX-51 | Unitario | FR-10, AC-10.2 | Probar registro para `INVALID_NODE`, `NO_ROUTE`, `CONTROLLER_UNAVAILABLE` e `INTERNAL_ERROR` mediante casos separados. | Se intenta persistir exactamente un resultado por cada solicitud válida fallida; se comprueban los cinco estados. El fallo de persistencia se cubre por separado en TX-53 y TX-55. |
| TX-52 | Unitario/DAO | FR-10, AC-10.3, NFR-09 | Construir `ForwardingService` con cliente y DAO falsos, sin servidor ni archivo real. | La prueba puede completar y observar llamadas/resultado sin dependencias externas. |
| TX-53 | Unitario/error | FR-10, CT-31 | Hacer que `ForwardingLogDAO.save()` falle tras un reenvío determinable. | HTTP `500`, `INTERNAL_ERROR`, incluye `packet_id` según contrato; no afirma persistencia; el Router sigue activo. |
| TX-54 | DAO | FR-10 | Escribir y volver a leer líneas del archivo JSONL usando un archivo temporal. | Cada resultado se serializa como un objeto JSON por línea; se puede recuperar/validar; no se corrompen registros previos. |
| TX-55 | DAO/error | FR-10 | Configurar una ruta de log sin permisos o un DAO que lance error de E/S. | La persistencia falla de forma controlada y la API devuelve `500 INTERNAL_ERROR`, sin revelar detalles internos. |
| TX-69 | Unitario/contrato | FR-09, FR-10, CT-37, A-07 | Inyectar una excepción interna inesperada en `ForwardingService` después de la validación local, con DAO de registro operativo. | HTTP `500 INTERNAL_ERROR` con `packet_id`; se intenta persistir un `ForwardingResult` con `status=INTERNAL_ERROR`; no se exponen detalles internos. |
| TX-56 | Contrato | FR-09, NFR-06, CT-18 | Detener Controller y solicitar `GET /health` al Router. | HTTP `200`, `status="ok"`, `application="router"`; no depende del Controller. |
| TX-57 | Integración | FR-09, NFR-06, NFR-11 | Con Controller detenido, enviar 10 solicitudes válidas independientes a `POST /packets`; medir tiempo de cada respuesta. | Cada solicitud responde `503 CONTROLLER_UNAVAILABLE` en ≤3 s si la persistencia funciona; Router sigue respondiendo a `/health`. Registrar las diez latencias. |
| TX-58 | Integración | FR-09, NFR-06, NFR-11 | Restaurar Controller después de TX-57 y enviar otro paquete válido. | El Router procesa el siguiente paquete sin reiniciarse; resultado conforme a la ruta vigente. |
| TX-59 | Configuración | NFR-05 | Arrancar Router con puerto alternativo, URL de Controller alternativa y archivo de log temporal. | Configuración aplicada sin editar código; Router se comunica con el Controller configurado. |
| TX-60 | Arquitectura | NFR-01, NFR-02, NFR-03, NFR-07, NFR-09 | Inspeccionar capas y construir `ForwardingService` con dependencias inyectadas. | Controlador HTTP no simula saltos; servicio no abre archivos ni instancia cliente/DAO concretos; lógica de reenvío reside en `ForwardingService`. |

## 8\. Pruebas de integración extremo a extremo

Ejecutar con los dos procesos reales, T1 y un directorio de resultados aislado. Cada paso debe registrar la solicitud, el estado HTTP, el cuerpo relevante y el estado/versionado observado.

| ID | Secuencia | Resultado esperado |
| :---- | :---- | :---- |
| TX-61 | `GET /health` en Controller y Router. | Ambos responden `200` con el identificador de aplicación correcto. |
| TX-62 | `POST /packets` A→D con `delay`. | `200 DELIVERED`; ruta `A-B-D`, costo `20`, versión `1`; un registro persistido. |
| TX-63 | `POST /links/fail` B–D y luego `POST /packets` A→D. | Falla confirmada, versión `2`; Router recibe ruta `A-C-D`, costo `35`, versión `2`. |
| TX-64 | Fallar C–D y luego enviar paquete A→D. | Versión `3`; `404 PATH_NOT_FOUND`; se intenta persistir `NO_ROUTE`. |
| TX-65 | Restaurar B–D y luego enviar paquete A→D. | Versión `4`; se vuelve a encontrar la ruta mínima A–B–D. |
| TX-66 | Detener Controller, enviar paquete y consultar `/health` de Router. | `503 CONTROLLER_UNAVAILABLE` dentro del umbral aprobado; Router responde `200` en `/health`. |
| TX-67 | Volver a iniciar Controller y enviar paquete válido. | El Router se recupera sin reinicio; la solicitud nueva se procesa correctamente. |
| TX-68 | Enviar entrada inválida al Router y revisar DAO/archivo de log. | `400 INVALID_INPUT`; no hubo consulta al Controller ni nuevo registro. |

## 9\. Pruebas no funcionales

### 9.1 NFR-01 a NFR-03, NFR-07 y NFR-09 — Arquitectura y modularidad

Las comprobaciones TX-34 y TX-60 se complementan con revisión de código. Debe verificarse que:

- Los modelos representan el dominio; los esquemas de Vista validan/serializan; los controladores HTTP delegan; los servicios contienen la lógica de aplicación.  
- Los servicios dependen de interfaces DAO/cliente, no de implementaciones concretas.  
- Ningún servicio o controlador abre directamente archivos de topología o de resultados.  
- Dijkstra se encuentra en `RoutingService`; la simulación de saltos en `ForwardingService`.  
- NetworkX se usa solo en Controller; Router no recalcula rutas.  
- Los DAOs y el cliente HTTP se inyectan desde el Composition Root.

La revisión debe guardar lista de módulos inspeccionados, regla, evidencia (archivo/línea o salida de herramienta) y resultado. Una afirmación general sin evidencia no basta para marcar el requisito como cumplido.

### 9.2 NFR-04 — Cobertura de contrato

Ejecutar todos los casos de contrato aplicables y verificar el mapeo `CT → TC` de la sección 10\. Cada endpoint público de 04 debe tener al menos una prueba que compruebe estado y campos; también deben cubrirse las variantes de error, esquemas y efectos observables. Un endpoint con prueba solo de camino exitoso no demuestra cobertura de sus errores documentados.

### 9.3 NFR-05 — Configuración

TX-36 y TX-59 deben ejecutarse con valores diferentes de los predeterminados. Registrar los valores efectivos de puertos, URL, timeout y archivos. La prueba falla si requiere modificar código fuente para cambiar configuración.

### 9.4 NFR-06 — Continuidad

Después de cada error esperado de ejecución, hacer una solicitud posterior a `GET /health` en la aplicación correspondiente. Debe responder `200` si el proceso se inició correctamente y sigue activo. Esta regla no aplica a errores fatales de inicialización del Controller con topología inválida, que deben impedir el arranque.

### 9.5 NFR-10 — Rendimiento de `GET /route`

**Estado del umbral:** aprobado por ambos integrantes el 27 de octubre de 2026, conforme a `01-requirements.md` y `05-implementation-plan.md`.

**Método de medición:** conservar las muestras de latencia HTTP completa y calcular p95 mediante nearest-rank: ordenar las 100 muestras y tomar el valor de rango `ceil(0,95 × n)`, es decir, la muestra 95. Registrar topología, entorno, latencias individuales y p95 obtenido para cada métrica.

**Interpretación:** hasta que se ejecuten y documenten las pruebas frente al umbral aprobado de 200 ms, el resultado se informa como medición descriptiva. La conformidad de NFR-10 se declara solo después de revisar los resultados frente al umbral aprobado.



### 9.6 NFR-11 — Resiliencia ante caída del Controller

**Estado del umbral:** aprobado por ambos integrantes el 27 de octubre de 2026, conforme a `01-requirements.md` y `05-implementation-plan.md`.

**Método de medición:** ejecutar los diez intentos especificados, registrar el tiempo de cada respuesta, verificar el estado HTTP, comprobar la respuesta de `GET /health` del Router y probar la recuperación después de reiniciar el Controller.

**Interpretación:** hasta que se ejecuten y documenten las pruebas frente al umbral aprobado de 3 segundos, las latencias obtenidas se informan como mediciones descriptivas. Un fallo de persistencia del resultado se clasifica conforme al contrato API y no se contabiliza como una respuesta satisfactoria de `503 CONTROLLER_UNAVAILABLE`.



## 10. Mapeo de casos de contrato CT a pruebas TX

El siguiente mapeo evita confundir los identificadores `CT` de 04 con los `TC` de esta especificación. Los casos pueden cubrir más de una comprobación de contrato, pero cada comprobación debe tener evidencia ejecutable.

| Comprobación en 04 | Prueba(s) en 06 | Cobertura |
| :---- | :---- | :---- |
| CT-01 | TX-18, TX-61 | Salud del Controller. |
| CT-02, CT-27 | TX-01, TX-19 | Topología y esquema. |
| CT-03, CT-06 | TX-11, TX-13, TX-20 | Ruta `delay` y valor predeterminado. |
| CT-04 | TX-14 | Costo `bandwidth`. |
| CT-05 | TX-15 | Costo `loss` y tolerancia numérica. |
| CT-07 | TX-12 | Origen igual a destino. |
| CT-08, CT-09 | TX-21, TX-22 | Validación de parámetros. |
| CT-10, CT-11 | TX-10, TX-23, TX-24 | Nodo inexistente frente a camino ausente. |
| CT-12, CT-13 | TX-25, TX-26 | Falla e idempotencia. |
| CT-14, CT-35 | TX-29 | Enlace inexistente/extremos inválidos. |
| CT-15, CT-29 | TX-30 | Cuerpo inválido. |
| CT-16, CT-28 | TX-27, TX-28 | Restauración e idempotencia. |
| CT-17 | TX-29 | Restaurar enlace inexistente. |
| CT-18 | TX-56, TX-61 | Salud del Router. |
| CT-19, CT-20 | TX-37, TX-38, TX-62 | Reenvío exitoso e ID generado. |
| CT-21, CT-30 | TX-41, TX-68 | Entrada inválida sin consulta ni registro. |
| CT-22, CT-36 | TX-42 | Métrica/ID inválidos. |
| CT-23 | TX-43 | Nodo inexistente en Router y registro `INVALID_NODE`. |
| CT-24 | TX-44, TX-64 | Camino ausente y registro `NO_ROUTE`. |
| CT-25 | TX-45, TX-57, TX-66 | Controller detenido y resiliencia. |
| CT-26, CT-32 | TX-47, TX-48 | Respuesta incompatible/no reconocida. |
| CT-31 | TX-53, TX-55 | Fallo de persistencia, separado de la excepción interna. |
| CT-37 | TX-69 | Excepción interna inesperada en POST /packets con packet_id y estado persistido INTERNAL_ERROR si el DAO funciona. |
| CT-33, CT-34 | TX-35 | Error interno en `/route` y `/topology`, sin filtración de detalles. |

Si una versión aprobada de 04 cambia los CT o su semántica, debe actualizarse esta tabla mediante control de cambios. Los CT duplicados o las referencias a endpoints incorrectos en la versión de origen deben corregirse documentalmente, no ocultarse en esta especificación.

## 11\. Matriz de trazabilidad FR/NFR a pruebas

| Requisito | Pruebas principales | Evidencia de aceptación |
| :---- | :---- | :---- |
| FR-01 — Carga y validación de topología | TX-01–TX-08, TX-32, TX-33 | Carga válida, rechazo de cada regla inválida, inicio fallido y reinicialización. |
| FR-02 — Topologías arbitrarias | TX-09, TX-10 | T1/T2 y grafo desconectado. |
| FR-03 — Dijkstra | TX-10–TX-12, TX-23–TX-24, TX-31 | Camino mínimo, origen=destino y errores diferenciados. |
| FR-04 — Métricas | TX-13–TX-17 | Fórmulas verificadas y exclusión de `p=1`. |
| FR-05 — API del Controller | TX-18–TX-24, TX-35 | Estados, esquemas y errores de `/health`, `/topology`, `/route`. |
| FR-06 — Falla/restauración | TX-25–TX-33, TX-63–TX-65 | Estado, ruta posterior, idempotencia, versión y archivo inmutable. |
| FR-07 — Router consulta Controller | TX-39–TX-40, TX-43–TX-49 | Una consulta por paquete válido; clasificación de respuestas; no hay cálculo local. |
| FR-08 — Simulación de reenvío | TX-37–TX-40, TX-62–TX-65 | `DELIVERED`, traza igual a ruta recibida y secuencia de saltos. |
| FR-09 — Errores controlados | TX-21–TX-24, TX-29–TX-30, TX-35, TX-41–TX-49, TX-56–TX-58, TX-66–TX-67 | Códigos correctos y continuidad del proceso. |
| FR-10 — Registro mediante DAO | TX-41–TX-55, TX-62–TX-68 | Un intento de registro por paquete válido, ausencia de registro en 400 y fallo de persistencia controlado. |
| NFR-01 — MVC | TX-34, TX-60 y revisión de código | Separación modelo/vista/controlador/servicios en ambas aplicaciones. |
| NFR-02 — DAO | TX-34, TX-52, TX-60 | Servicios usan interfaces y no acceden directamente a archivos. |
| NFR-03 — Algoritmos fuera de controladores | TX-34, TX-40, TX-60 | Dijkstra en `RoutingService`, reenvío en `ForwardingService`. |
| NFR-04 — Contrato API | TX-18–TX-30, TX-35, TX-37–TX-49, TX-56 y mapeo CT→TC | Todos los endpoints y variantes de error cubiertos. |
| NFR-05 — Configuración | TX-36, TX-59 | Arranque con valores alternativos sin editar código. |
| NFR-06 — Continuidad | TX-02–TX-03 (fallo de inicio esperado), TX-35, TX-45–TX-49, TX-53, TX-56–TX-58 | Errores en ejecución no detienen procesos; configuración inválida sí impide iniciar Controller. |
| NFR-07 — Inyección de dependencias | TX-34, TX-52, TX-60 | Dependencias inyectadas; sin construcción interna de DAO/cliente concreto en servicios. |
| NFR-08 — Trazabilidad | Esta matriz y sección 12 | Todos los FR/NFR enlazados con pruebas o revisión verificable. |
| NFR-09 — Sustitución por fakes/mocks | TX-34, TX-52, TX-60 | Pruebas unitarias sin servidor HTTP ni archivos reales cuando corresponda. |
| NFR-10 — Rendimiento | Protocolo de sección 9.5 | 100 muestras por métrica, p95 documentado y umbral aprobado antes de declarar cumplimiento. |
| NFR-11 — Resiliencia | TX-57, TX-66–TX-67 y protocolo 9.6 | Diez intentos con Controller caído, ≤3 s por intento si se aprueba el umbral, salud y recuperación. |

## 12. Criterios globales de aceptación

La aceptación de la implementación y de los resultados se evaluará con los siguientes criterios verificables. La aprobación de la línea base documental no equivale a la aprobación de resultados de pruebas.

1. Los casos obligatorios están ejecutados y su registro contiene fecha/hora, versión de código, entorno, datos, resultado y evidencia reproducible.
2. Para cumplir el criterio deben existir al menos 8 pruebas ejecutadas con resultado APROBADA, incluyendo TC-08 y TC-09 del PDF (implementados por TX-34 y TX-52, respectivamente: `RoutingService` con `TopologyDAO` falso y `ForwardingService` con su DAO de registro, sin servidor HTTP).
3. La revisión de código de ambos controladores confirma que no contienen Dijkstra ni la lógica de simulación de saltos; el Router no calcula rutas localmente.
4. Se realiza una demostración en vivo de los dos procesos independientes, reenvío exitoso, falla y restauración de enlaces, error de Controller y recuperación, y uso de dependencias sustitutas.
5. Las incidencias encontradas están documentadas con identificador, impacto, responsable y prueba de regresión cuando corresponda.
6. NFR-10 y NFR-11 se evalúan contra los umbrales aprobados y solo se declaran conformes cuando exista evidencia de ejecución y resultados documentados.

Actualmente, todos los casos figuran como NO EJECUTADA en el Registro de ejecución. No se afirma que exista ninguna prueba ejecutada, aprobada o fallida.

## 13. Decisiones cerradas y trazabilidad

Las siguientes decisiones forman parte de la línea base aprobada el 27 de octubre de 2026. Se mantienen los IDs CT para comprobaciones del contrato y TX para casos detallados de prueba; TC-01 a TC-09 se reservan al significado fijo del PDF del taller.

1. **INTERNAL_ERROR y A-07/R-03 (CH-02).** ForwardingStatus contiene cinco estados: DELIVERED, INVALID_NODE, NO_ROUTE, CONTROLLER_UNAVAILABLE e INTERNAL_ERROR. Una excepción interna inesperada posterior a la validación local genera un intento de ForwardingResult con estado INTERNAL_ERROR y una respuesta HTTP 500 INTERNAL_ERROR con packet_id. El estado persistido y el código HTTP comparten nombre, pero son conceptos distintos. El fallo de persistencia se verifica aparte en TX-53 y TX-55; la excepción interna se verifica en TX-69/CT-37.
2. **Presencia de packet_id (CH-02).** Los errores posteriores a la validación local incluyen packet_id cuando está disponible; los errores de validación local HTTP 400 no generan registro ni requieren packet_id en ErrorResponse.
3. **Nombres de componentes (CH-05).** Se usan FileTopologyDAO, LinkManagementService y TopologyQueryService conforme a la línea base documental.
4. **CT-37 (CH-04).** CT-37 define exclusivamente la excepción interna inesperada de POST /packets, con HTTP 500 INTERNAL_ERROR y packet_id. CT-31 se conserva para el fallo de ForwardingLogDAO.save. CT-33 y CT-34 cubren errores internos de GET /route y GET /topology, respectivamente. No hay duplicación semántica entre esos CT.
5. **Umbrales NFR-10/NFR-11 (CH-03).** NFR-10 queda fijado en p95 ≤ 200 ms para GET /route con la carga descrita; el p95 se calcula por nearest-rank. NFR-11 queda fijado en respuesta de POST /packets en ≤ 3 segundos con el Controller detenido, bajo timeout de 2 segundos más margen de 1 segundo. La aprobación de umbrales no significa que sus pruebas se hayan ejecutado.
6. **Método de percentil (CH-03).** Se usa nearest-rank, con rango `ceil(0,95 × n)`; para las 100 muestras de cada métrica, el p95 es la muestra ordenada número 95.
7. **Referencias de pruebas (CH-04).** Los documentos 01 a 05 utilizan TX-xx para referirse a casos detallados de este documento. TC-01 a TC-09 mantienen exclusivamente el significado del PDF y se vinculan con los TX correspondientes en §5.5 y §10.
8. **Registro de ejecución (CH-05).** Todos los casos comienzan en estado NO EJECUTADA. Ningún resultado se infiere de la existencia de una especificación ni de la aprobación documental.

## 14\. Ejecución, registro y reporte de resultados

### 14.1 Registro por caso

Por cada ejecución se debe guardar:

| Campo | Contenido |
| :---- | :---- |
| ID de prueba | `TC-xx` para los casos del PDF; `TX-xx` para los casos detallados. |
| Fecha/hora | Inicio de la ejecución, con zona horaria identificada |
| Versión de código | Commit/hash o versión del repositorio |
| Entorno | Python, dependencias, sistema operativo y configuración relevante |
| Datos | T1–T6 o fixture identificado y versión/hash cuando corresponda |
| Resultado | APROBADA, FALLIDA, BLOQUEADA o NO EJECUTADA |
| Evidencia | Salida de pytest, request/response sanitizada, estado del DAO o log |
| Incidencia | ID de incidencia/tarea correctiva si falla |
| Ejecutor/revisor | Persona que ejecutó y persona que revisó |

### 14.1.1 Registro de ejecución

El registro inicial refleja el estado documental real: todas las pruebas están NO EJECUTADA. Los campos no disponibles se mantienen como `—`; no se inventan fechas, versiones, evidencias ni ejecutores.

| ID de prueba | Fecha/hora | Versión de código | Entorno | Datos | Resultado | Evidencia | Incidencia | Ejecutor/revisor |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| TC-01 | — | — | — | — | NO EJECUTADA | — | — | — |
| TC-02 | — | — | — | — | NO EJECUTADA | — | — | — |
| TC-03 | — | — | — | — | NO EJECUTADA | — | — | — |
| TC-04 | — | — | — | — | NO EJECUTADA | — | — | — |
| TC-05 | — | — | — | — | NO EJECUTADA | — | — | — |
| TC-06 | — | — | — | — | NO EJECUTADA | — | — | — |
| TC-07 | — | — | — | — | NO EJECUTADA | — | — | — |
| TC-08 | — | — | — | — | NO EJECUTADA | — | — | — |
| TC-09 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-01 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-02 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-03 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-04 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-05 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-06 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-07 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-08 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-09 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-10 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-11 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-12 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-13 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-14 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-15 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-16 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-17 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-18 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-19 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-20 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-21 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-22 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-23 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-24 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-25 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-26 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-27 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-28 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-29 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-30 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-31 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-32 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-33 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-34 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-35 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-36 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-37 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-38 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-39 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-40 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-41 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-42 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-43 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-44 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-45 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-46 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-47 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-48 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-49 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-50 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-51 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-52 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-53 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-54 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-55 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-56 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-57 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-58 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-59 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-60 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-61 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-62 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-63 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-64 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-65 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-66 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-67 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-68 | — | — | — | — | NO EJECUTADA | — | — | — |
| TX-69 | — | — | — | — | NO EJECUTADA | — | — | — |

### 14.2 Comandos de referencia

Los comandos de referencia deben coincidir con la estructura del repositorio entregado; permiten ejecución selectiva por nivel:

```sh
pytest -q tests/unit
pytest -q tests/contract
pytest -q tests/integration
pytest -q tests/architecture
pytest -q
```

Si la estructura real del repositorio difiere, actualizar estos comandos en el README y en este documento mediante control de cambios. No registrar un comando como evidencia si no se ejecutó realmente.

### 14.3 Regresión y cierre

- Ejecutar la suite completa después de cualquier cambio de contrato, modelo, error, algoritmo, persistencia o configuración.  
- Cada incidencia debe tener una prueba de regresión cuando sea técnicamente posible.  
- Conservar fallos originales y sus correcciones; no eliminar del reporte una ejecución fallida.  
- Revisar el mapeo de trazabilidad cuando se agreguen o retiren requisitos, endpoints o casos de contrato.  
- El cierre se firma solo después de que los casos obligatorios estén ejecutados y las excepciones estén aprobadas explícitamente.

## 15\. Control de cambios y aprobación

### 15.1 Registro de versiones

| Versión | Fecha | Descripción | Autores |
| :---- | :---- | :---- | :---- |
| 1.0 | 22 de octubre de 2026 | Primera especificación formal de pruebas derivada de los entregables 01–05; define niveles, datos, casos detallados y trazabilidad CT→pruebas. | Andrés Felipe Mateus y Santiago Cavarro |
| 1.2 | 27 de octubre de 2026 | TC-01 a TC-09 reservados al PDF; casos detallados renombrados TX-01 a TX-69; INTERNAL_ERROR, CT-37, registro de ejecución y aprobación sincronizados. | Andrés Felipe Mateus y Santiago Cavarro |

### 15.2 Cambios posteriores al congelamiento

| ID | Fecha | Motivo | Casos/documentos afectados | Aprobación |
| :---- | :---- | :---- | :---- | :---- |
| CH-02 | 27 de octubre de 2026 | Se incorpora INTERNAL_ERROR como quinto estado y se separa del fallo de persistencia. | 01, 02, 03, 04, 05, 06 | Aprobado, 27 de octubre de 2026 — ambos integrantes |
| CH-03 | 27 de octubre de 2026 | Se aprueban configuración por variables de entorno, umbrales NFR-10/NFR-11 y método nearest-rank; no se inventan resultados de ejecución. | 01, 04, 05, 06 | Aprobado, 27 de octubre de 2026 — ambos integrantes |
| CH-04 | 27 de octubre de 2026 | CT-37 define la excepción interna de POST /packets; TC del PDF se separan de TX detallados. | 01, 03, 04, 05, 06 | Aprobado, 27 de octubre de 2026 — ambos integrantes |
| CH-05 | 27 de octubre de 2026 | Se añade registro de ejecución inicial con todos los casos NO EJECUTADA y se corrigen referencias/encabezados. | 01, 02, 03, 04, 05, 06 | Aprobado, 27 de octubre de 2026 |

### 15.3 Aprobación de la línea base

| Integrante | Rol | Confirmación | Fecha |
| :---- | :---- | :---- | :---- |
| Andrés Felipe Mateus | Controller | Aprobado, 27 de octubre de 2026 | 27 de octubre de 2026 |
| Santiago Cavarro | Router | Aprobado, 27 de octubre de 2026 | 27 de octubre de 2026 |

La aprobación de esta especificación y de la línea base no implica que las pruebas hayan sido ejecutadas. Los umbrales NFR-10 y NFR-11 están aprobados; sus resultados solo podrán aceptarse tras ejecución y revisión documentadas.

No se declarará verificado el sistema hasta disponer de resultados de pruebas ejecutadas, evidencia reproducible y resolución documentada de los defectos bloqueantes.




