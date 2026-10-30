# INFORMÁTICA PARA LAS TELECOMUNICACIONES

## Taller de Desarrollo Dirigido por Especificaciones (SDD) e Ingeniería de Prompts

# Especificación de requisitos de software

Solución educativa tipo SDN: Controller y Router

| Campo | Detalle |
| :---- | :---- |
| Proyecto | Aplicaciones Controller y Router comunicadas por REST/JSON (simulación a nivel de aplicación) |
| Documento | specs/01-requirements.md |
| Versión | 1.2 |
| Fecha | 27 de octubre de 2026 |
| Estado | Línea base aprobada |
| Controller (Estudiante A) | Andrés Felipe Mateus |
| Router (Estudiante B) | Santiago Cavarro |

---

## 1\. Introducción

### 1.1 Propósito

Este documento especifica qué debe hacer el sistema y bajo qué restricciones de calidad debe hacerlo. No describe cómo se construye ni contiene código de implementación. Es la base de los documentos 02 a 06 y de la implementación de la Sesión 2.

Cada requisito tiene un identificador único, criterios de aceptación verificables y trazabilidad hacia casos de uso y pruebas. Las referencias a tareas y pruebas se vinculan con los identificadores definitivos IMP y TX/TC de los documentos 05 y 06.

### 1.2 Alcance

El sistema está formado por dos aplicaciones Python independientes, ejecutadas como procesos separados, que se comunican mediante REST/JSON:

- Controller: gestiona la topología de red, calcula las rutas de costo mínimo y administra la falla y restauración de enlaces.  
- Router: recibe paquetes simulados, solicita la ruta al Controller, simula el reenvío salto a salto y registra el resultado.

Dentro del alcance:

- Carga y validación de topologías JSON.  
- Enrutamiento con Dijkstra y tres métricas de costo.  
- API REST documentada.  
- Falla y restauración de enlaces.  
- Reenvío simulado.  
- Registro de resultados.  
- Manejo controlado de errores.  
- Pruebas automatizadas y revisiones de arquitectura.

Fuera del alcance:

- Protocolo OpenFlow y despliegue en producción.  
- Transmisión de tráfico de red real.  
- Autenticación y autorización.  
- Interfaz gráfica.  
- Base de datos.  
- Múltiples Routers concurrentes como parte del escenario requerido.  
- Pérdida aleatoria de paquetes durante el reenvío.  
- Maximización del ancho de banda del cuello de botella.

### 1.3 Definiciones y abreviaturas

| Término | Definición |
| :---- | :---- |
| SDN | Redes definidas por software: el plano de control (decisiones de ruta) está separado del plano de reenvío. |
| Controller | Aplicación que mantiene la topología y decide las rutas. |
| Router | Aplicación que reenvía paquetes siguiendo la ruta decidida por el Controller; no calcula rutas. |
| Topología | Conjunto de nodos y enlaces que representa la red. |
| Enlace | Conexión no dirigida entre dos nodos, con retardo, ancho de banda, probabilidad de pérdida y estado operativo. |
| Métrica / costo | Criterio de optimización (delay, bandwidth o loss) y valor no negativo asignado a cada enlace para Dijkstra. |
| Versión de topología | Entero que identifica el estado de la topología durante una ejecución del Controller; aumenta con cada cambio efectivo del estado de un enlace. |
| Traza | Lista ordenada de los nodos recorridos por un paquete durante el reenvío simulado. |
| DAO | Objeto de acceso a datos: abstracción que encapsula la obtención y el almacenamiento de datos. |
| MVC | Patrón Modelo–Vista–Controlador aplicado a ambas aplicaciones. |
| FR / NFR | Requisito funcional / requisito no funcional. |
| UC / AC / TC | Caso de uso / criterio de aceptación / caso de prueba. |



### 1.4 Convenciones

- Identificadores: FR-xx, NFR-xx, UC-xx, AC-xx.y (criterio y), TC-xx y A-xx para decisiones de interpretación.  
- Debe indica un requisito obligatorio. Todos los requisitos de este documento son obligatorios. Los umbrales NFR-10 y NFR-11 y los parámetros de configuración están aprobados como parte de la línea base.  
- Unidades: retardo en milisegundos (ms), ancho de banda en megabits por segundo (Mbps) y pérdida como probabilidad adimensional entre 0 y 1\.  
- Responsables: el Controller corresponde a Andrés Felipe Mateus y el Router a Santiago Cavarro. Los requisitos transversales son responsabilidad de ambos.  
- Los códigos de aplicación y los estados HTTP se consideran elementos distintos: un mismo estado HTTP puede acompañar códigos de aplicación diferentes, según el contrato definido en 04-api-contract.md.

---

## 2\. Descripción general

### 2.1 Perspectiva del sistema

El Router es el punto de entrada del tráfico simulado. Por cada paquete válido consulta al Controller mediante HTTP, recibe la ruta y simula el reenvío. El Controller es la única autoridad sobre la topología y las rutas.

Esta separación entre decisión (plano de control) y ejecución (plano de reenvío) es la propiedad esencial del estilo SDN que el sistema debe preservar. El Router no debe calcular rutas localmente, incluso cuando el Controller no esté disponible.

### 2.2 Actores y sistemas externos

| Actor / sistema | Descripción |
| :---- | :---- |
| Cliente / operador | Persona o script de prueba que envía paquetes al Router, consulta rutas y topología al Controller y solicita fallas o restauraciones de enlaces. |
| Router | Sistema que actúa como cliente HTTP del Controller. |
| Controller | Sistema que atiende las consultas de ruta y de estado de la topología, además de las operaciones de falla y restauración. |
| Almacenamiento | Archivo JSON de topología y archivo de registro de reenvíos, accedidos mediante sus respectivas abstracciones DAO. |

### 2.3 Restricciones y supuestos

- Python 3.11 o superior.  
- Uso de FastAPI, Uvicorn, NetworkX, pytest y un cliente HTTP.  
- Dos procesos independientes con puertos configurables; la comunicación entre aplicaciones se realiza mediante REST/JSON.  
- MVC y DAO deben ser visibles en ambas aplicaciones; se utiliza inyección de dependencias.  
- El Router no calcula rutas por sí mismo bajo ninguna circunstancia.  
- La solución es una simulación a nivel de aplicación; no se transmiten paquetes reales.  
- En la Sesión 1 no se genera código de implementación.  
- El Controller es la única autoridad para calcular rutas y mantener el estado operativo de los enlaces.  
- El archivo de topología es una fuente de configuración inicial; los cambios de estado de enlaces durante la ejecución no se persisten en ese archivo.

### 2.4 Datos de entrada: topología

La topología se carga desde un archivo JSON con una lista de nodos y una lista de enlaces. La estructura JSON exacta se especifica en 04-api-contract.md.

| Atributo | Unidad / tipo | Regla de validación |
| :---- | :---- | :---- |
| Identificador de nodo | Texto | No vacío y único dentro de la topología. |
| Extremos del enlace | Texto | Deben identificar dos nodos existentes y distintos; no se permiten bucles. |
| Unicidad del enlace | Par de nodos | No se permiten enlaces duplicados entre el mismo par, independientemente del orden de sus extremos. |
| Retardo (d) | ms | d \>= 0\. |
| Ancho de banda (b) | Mbps | b \> 0\. |
| Pérdida (p) | Probabilidad | 0 \<= p \<= 1\. Si p \= 1, el enlace es inutilizable para el enrutamiento. |
| Estado operativo | Activo / fallado | Todos los enlaces comienzan activos al cargar la topología. |

Estado inicial y estado operativo de los enlaces

El archivo JSON define la topología y los atributos de sus enlaces, pero no determina el estado operativo inicial. Al iniciar el Controller, todos los enlaces se establecen como activos y topology\_version comienza en 1\. El estado de falla o restauración se mantiene en memoria y puede modificarse mediante la API.

Un enlace con probabilidad de pérdida p \= 1 se considera inutilizable para el enrutamiento, aunque su estado operativo sea activo. Si el esquema JSON incluye un atributo de estado, este no debe sobrescribir la regla de inicialización descrita aquí.

La versión identifica el estado de la topología únicamente durante una ejecución del proceso Controller. No es persistente ni garantiza unicidad entre ejecuciones distintas. El reinicio del Controller vuelve a cargar el archivo original, activa todos los enlaces y reinicia la versión a 1\.

### 2.5 Parámetros de configuración

La configuración se realiza mediante variables de entorno; los nombres y valores predeterminados aprobados se especifican en 05-implementation-plan.md.

| Parámetro | Aplicación | Descripción | Valor predeterminado |
| :---- | :---- | :---- | :---- |
| controller\_port | Controller | Puerto de escucha del Controller. | 8001. |
| router\_port | Router | Puerto de escucha del Router. | 8002. |
| topology\_file\_path | Controller | Ubicación del archivo JSON de topología. | data/topology.json. |
| controller\_base\_url | Router | Dirección base HTTP del Controller. | http://127.0.0.1:8001. |
| controller\_timeout\_seconds | Router | Tiempo máximo de espera por el Controller. | 2 segundos. |
| forwarding\_log\_path | Router | Ubicación del archivo de registro de reenvíos. | logs/forwarding.jsonl. |



**Configuración aprobada**

Configuración aprobada, 27 de octubre de 2026: Controller en puerto 8001; Router en puerto 8002; timeout del Controller de 2 segundos; un único intento HTTP sin reintentos automáticos; topología en `data/topology.json`; registro en `logs/forwarding.jsonl`. Todos los parámetros siguen siendo configurables conforme a NFR-05.





### 2.6 Catálogo de errores

Los errores esperados se devuelven como JSON con un código de aplicación y un mensaje. El formato exacto se define en 04-api-contract.md.

| Código de aplicación | HTTP | Condición | Origen |
| :---- | ----: | :---- | :---- |
| INVALID\_INPUT | 400 | Parámetros ausentes o mal formados, métrica no soportada o cuerpo JSON inválido. | Controller y Router. |
| NODE\_NOT\_FOUND | 404 | El nodo origen o destino no existe en la topología. | Controller; Router conserva el significado de la respuesta válida del Controller. |
| LINK\_NOT\_FOUND | 404 | El enlace indicado para fallar o restaurar no existe. | Controller. |
| PATH\_NOT\_FOUND | 404 | Los nodos existen, pero no hay camino utilizable entre ellos con los enlaces operativos y elegibles. | Controller; Router conserva el significado de la respuesta válida del Controller. |
| CONTROLLER\_UNAVAILABLE | 503 | El Router no puede comunicarse con el Controller, agota el tiempo de espera o recibe una respuesta inválida o incompatible con el contrato. | Router. |
| INTERNAL\_ERROR | 500 | Error interno inesperado o fallo de persistencia del registro; la respuesta no expone detalles internos. | Controller y Router. |

Reglas de clasificación de errores

- Los errores de validación de una solicitud se devuelven como 400 INVALID\_INPUT.  
- Los errores de aplicación válidos del Controller, como 404 NODE\_NOT\_FOUND y 404 PATH\_NOT\_FOUND, conservan su significado cuando el Router los recibe.  
- Los errores de transporte, los tiempos de espera y las respuestas del Controller que sean inválidas o incompatibles con el contrato se convierten en 503 CONTROLLER\_UNAVAILABLE.  
- Un fallo al persistir un resultado de reenvío produce 500 INTERNAL\_ERROR. El Router no debe indicar que el resultado quedó almacenado si el DAO no confirmó la operación.  
- Los errores no deben provocar la terminación del proceso una vez que la aplicación ha iniciado correctamente. Los errores fatales de inicialización, como una topología inexistente o inválida, sí impiden el arranque del Controller.

### 2.7 Ambigüedades identificadas y decisiones del equipo

Durante el análisis del enunciado se identificaron los siguientes puntos ambiguos. Las decisiones forman parte de la línea base aprobada y deben mantenerse consistentes en los documentos de arquitectura, contrato, implementación y pruebas.

| ID | Ambigüedad | Decisión y justificación | Requisitos relacionados |
| :---- | :---- | :---- | :---- |
| A-01 | Cómo distinguir nodo inválido de ausencia de camino. | Las entradas mal formadas producen 400 INVALID\_INPUT; un nodo inexistente produce 404 NODE\_NOT\_FOUND; los nodos existentes sin camino utilizable producen 404 PATH\_NOT\_FOUND. El código de aplicación permite distinguir las condiciones. | FR-03, FR-09 |
| A-02 | Tratamiento de valores límite de los atributos del enlace. | Se aceptan d \>= 0, b \> 0 y 0 \<= p \<= 1; cualquier otro valor rechaza la carga. Un enlace con p \= 1 se excluye del cálculo para todas las métricas porque se considera inutilizable y evita evaluar \-ln(0). | FR-01, FR-04 |
| A-03 | Topología dirigida o no dirigida. | La topología es no dirigida. Un enlace es un par no ordenado de nodos; fallar o restaurar afecta ambos sentidos. | FR-02, FR-06 |
| A-04 | Nombres y valor predeterminado de la métrica. | Los valores son delay, bandwidth (costo 1/b) y loss (costo \-ln(1-p)). El parámetro es opcional y por defecto es delay, conforme al ejemplo del enunciado. | FR-04, FR-05, FR-07 |
| A-05 | Persistencia del estado de falla y repetición de operaciones. | El estado operativo de los enlaces vive solo en memoria. Al reiniciar el Controller, todos los enlaces vuelven a estar activos y la versión vuelve a 1\. Fallar un enlace ya fallado o restaurar uno activo es idempotente: responde 200 sin cambiar la versión. La versión solo aumenta con un cambio efectivo del estado de un enlace. | FR-06 |
| A-06 | Alcance de la simulación de reenvío. | El reenvío es determinista: recorre la ruta recibida sin esperas reales ni descartes aleatorios. La pérdida p solo influye en el costo de enrutamiento. La ruta es una instantánea del momento de la consulta; fallas posteriores afectan a paquetes siguientes. | FR-07, FR-08 |
| A-07 | Qué se registra y dónde. | El Router utilizará los siguientes estados para clasificar los resultados de las operaciones de forwarding: DELIVERED: el paquete fue procesado y entregado correctamente según el modelo de simulación. INVALID\_NODE: la solicitud contiene un nodo inválido conforme a las reglas de validación. NO\_ROUTE: no existe una ruta utilizable para el destino solicitado. CONTROLLER\_UNAVAILABLE: no fue posible obtener la información de enrutamiento requerida debido a la indisponibilidad del Controller. INTERNAL\_ERROR: ocurrió una excepción interna inesperada durante el procesamiento de una solicitud validada. Se registrará un resultado por cada solicitud bien formada, incluidos los resultados fallidos. Las solicitudes mal formadas que generen HTTP 400 no se registrarán. El estado representa el resultado del procesamiento, no el estado del almacenamiento. El estado persistido INTERNAL_ERROR y el código HTTP 500 INTERNAL_ERROR comparten nombre, pero son conceptos distintos. Si ocurre un fallo de persistencia, este deberá registrarse por separado. El Router no deberá considerar exitosa una escritura sin confirmación del repositorio. El almacén predeterminado será un archivo local configurable. Las pruebas podrán utilizar un DAO en memoria. | FR-10 |
| A-08 | Qué reporta GET /health del Router. | Solo informa de la disponibilidad del propio Router; no depende del Controller. El Router debe seguir respondiendo a su comprobación de salud cuando el Controller esté caído. | FR-05, NFR-06, NFR-11 |
| A-09 | Varios caminos con el mismo costo mínimo. | Cualquier camino de costo mínimo es válido. Las pruebas de aceptación usarán topologías con mínimo único cuando sea necesario comprobar una ruta exacta. | FR-03, FR-04 |
| A-10 | Reintentos ante falla del Controller. | No hay reintentos automáticos. Se realiza un único intento con tiempo de espera configurable, de 2 segundos por defecto. | FR-09, NFR-11 |

---

## 3\. Casos de uso

### UC-01 · Consultar ruta

| Campo | Detalle |
| :---- | :---- |
| Actor | Cliente u operador; también el Router. |
| Precondición | El Controller está activo y tiene la topología cargada. |
| Flujo principal | 1\. El actor envía origen, destino y métrica opcional. 2\. El Controller valida las entradas. 3\. Calcula la ruta de costo mínimo sobre los enlaces activos y utilizables. 4\. Responde con la ruta, la métrica, el costo total y la versión de topología. |
| Flujos alternos | 2a. Entradas inválidas: 400 INVALID\_INPUT. 3a. Nodo inexistente: 404 NODE\_NOT\_FOUND. 3b. Sin camino utilizable: 404 PATH\_NOT\_FOUND. |
| Postcondición | El estado de la topología no cambia. |
| Requisitos | FR-02, FR-03, FR-04, FR-05, FR-09. |

### UC-02 · Reenviar paquete

| Campo | Detalle |
| :---- | :---- |
| Actor | Cliente. |
| Precondición | El Router está activo; para completar el flujo normal, el Controller también está activo. |
| Flujo principal | 1\. El cliente envía un paquete al Router. 2\. El Router valida el formato. 3\. Solicita la ruta al Controller por HTTP. 4\. Simula el reenvío salto a salto por la ruta recibida. 5\. Registra el resultado mediante ForwardingLogDAO. 6\. Responde con el estado DELIVERED, la ruta y la traza. |
| Flujos alternos | 2a. Formato inválido: 400 INVALID\_INPUT, sin registro. 3a. Nodo inexistente: 404 NODE\_NOT\_FOUND; se registra INVALID\_NODE. 3b. Sin camino: 404 PATH\_NOT\_FOUND; se registra NO\_ROUTE. 3c. Controller no disponible: se aplica UC-07 y se registra CONTROLLER\_UNAVAILABLE. 5a. Falla la persistencia del resultado: 500 INTERNAL\_ERROR; no se afirma que el registro quedó almacenado. |
| Postcondición | Se intenta registrar un resultado por cada paquete bien formado. Si la persistencia falla, la solicitud devuelve un error y no se considera confirmado el registro. |
| Requisitos | FR-07, FR-08, FR-09, FR-10. |

### UC-03 · Fallar enlace

| Campo | Detalle |
| :---- | :---- |
| Actor | Cliente u operador. |
| Precondición | El Controller está activo. |
| Flujo principal | 1\. El actor indica los dos extremos del enlace. 2\. El Controller marca el enlace como fallado. 3\. Incrementa la versión de topología si el estado cambió efectivamente. 4\. Responde confirmando el estado y la versión vigente. |
| Flujos alternos | 1a. Cuerpo inválido: 400 INVALID\_INPUT. 2a. Enlace inexistente: 404 LINK\_NOT\_FOUND. 2b. Enlace ya fallado: 200, sin cambio de versión. |
| Postcondición | Las consultas posteriores excluyen el enlace fallado. |
| Requisitos | FR-06. |

### UC-04 · Restaurar enlace

| Campo | Detalle |
| :---- | :---- |
| Actor | Cliente u operador. |
| Precondición | El Controller está activo. |
| Flujo principal | 1\. El actor indica los dos extremos del enlace. 2\. El Controller marca el enlace como activo. 3\. Incrementa la versión de topología si el estado cambió efectivamente. 4\. Responde confirmando el estado y la versión vigente. |
| Flujos alternos | 1a. Cuerpo inválido: 400 INVALID\_INPUT. 2a. Enlace inexistente: 404 LINK\_NOT\_FOUND. 2b. Enlace ya activo: 200, sin cambio de versión. |
| Postcondición | El enlace vuelve a ser elegible para el cálculo de rutas, salvo que tenga p \= 1, caso en el que sigue siendo inutilizable. |
| Requisitos | FR-06. |

### UC-05 · Consultar topología

| Campo | Detalle |
| :---- | :---- |
| Actor | Cliente u operador. |
| Precondición | El Controller está activo. |
| Flujo principal | 1\. El actor solicita la topología. 2\. El Controller devuelve los nodos, los enlaces con su estado operativo y la versión vigente. |
| Flujos alternos | 2a. Error inesperado: 500 INTERNAL\_ERROR. |
| Postcondición | El estado de la topología no cambia. |
| Requisitos | FR-01, FR-05. |

### UC-06 · Verificar disponibilidad

| Campo | Detalle |
| :---- | :---- |
| Actor | Cliente u operador. |
| Precondición | La aplicación consultada está en ejecución. |
| Flujo principal | 1\. El actor consulta el estado de salud. 2\. La aplicación responde 200, indicando que está disponible. |
| Flujos alternos | 1a. Aplicación detenida: no hay respuesta; el cliente detecta la situación. |
| Postcondición | El estado de la topología y los resultados de reenvío no cambian. |
| Requisitos | FR-05, NFR-06, NFR-11. |

### UC-07 · Tratar indisponibilidad del Controller

| Campo | Detalle |
| :---- | :---- |
| Actor | Router, a partir de una solicitud de un cliente. |
| Precondición | El Router está activo y el Controller no responde, agota el tiempo de espera o devuelve una respuesta inválida o incompatible con el contrato. |
| Flujo principal | 1\. El Router intenta obtener la ruta. 2\. Detecta la falla de comunicación o la respuesta inválida. 3\. Construye y registra el resultado CONTROLLER\_UNAVAILABLE. 4\. Responde 503 CONTROLLER\_UNAVAILABLE con un mensaje estable, siempre que el registro se haya persistido correctamente. 5\. Permanece activo. |
| Flujos alternos | 4a. Si falla la persistencia del registro, responde 500 INTERNAL\_ERROR y no afirma que el registro se guardó. 5a. Cuando el Controller vuelve a estar disponible, el siguiente paquete se procesa sin reiniciar el Router. |
| Postcondición | El Router sigue disponible. No calcula una ruta local ni requiere reinicio para recuperarse de la caída del Controller. |
| Requisitos | FR-09, FR-10, NFR-06, NFR-11. |

---

## 4\. Requisitos funcionales

### 4.1 Definición de métricas de costo

Dijkstra requiere costos no negativos. Las tres métricas definidas a continuación cumplen esa condición para los enlaces elegibles.

| Métrica | Costo de un enlace | Validez | Observación |
| :---- | :---- | :---- | :---- |
| delay | d | d \>= 0 | El costo total es el retardo acumulado. |
| bandwidth | 1/b | b \> 0 | Heurística aditiva; no equivale a maximizar el ancho de banda del cuello de botella. |
| loss | \-ln(1-p) | 0 \<= p \< 1 | Con pérdidas independientes, minimizar la suma equivale a maximizar la probabilidad de entrega. Si p \= 1, el enlace es inutilizable y se excluye de todas las métricas. |

El costo total de una ruta es la suma de los costos de sus enlaces. Para loss, si el costo total es C, entonces exp(-C) debe coincidir, dentro de la tolerancia numérica definida en las pruebas, con el producto de (1-p) de los enlaces de la ruta.

### 4.2 FR-01 · Carga de topología mediante DAO

| Campo | Detalle |
| :---- | :---- |
| Aplicación | Controller. |
| Descripción | El Controller debe cargar la topología desde un archivo JSON a través de la interfaz TopologyDAO y su implementación basada en archivo, validando el contenido según la sección 2.4. |
| Entradas | Ubicación configurable del archivo JSON. |
| Salidas | Topología en memoria con todos los enlaces activos y topology\_version \= 1\. |
| Errores | Archivo inexistente, JSON mal formado o datos inválidos: error de carga que identifica el campo o enlace afectado. El Controller no inicia y termina con un código de salida distinto de cero. |
| Criterios de aceptación | AC-01.1: Con un archivo válido, la topología cargada contiene exactamente los nodos y enlaces definidos. Todos los enlaces comienzan activos, independientemente de cualquier atributo de estado presente en el archivo. AC-01.2: Con d \< 0, b \<= 0, p fuera de \[0,1\], enlaces duplicados, bucles o nodos inexistentes, la carga se rechaza con un mensaje descriptivo. AC-01.3: RoutingService obtiene la topología solo mediante la interfaz TopologyDAO. |
| Pruebas / verificación | Prueba de carga y validación; revisión arquitectónica. La asignación de identificadores TC debe confirmarse en 06-test-specification.md. |

### 4.3 FR-02 · Soporte de topologías válidas arbitrarias con NetworkX

| Campo | Detalle |
| :---- | :---- |
| Aplicación | Controller. |
| Descripción | El Controller debe soportar topologías válidas de distinta estructura y conectividad, incluidos grafos desconectados, representadas mediante un grafo de NetworkX y sin lógica específica para una topología concreta. No se establece un límite funcional de tamaño; el rendimiento se verifica por separado mediante NFR-10. |
| Entradas | Topología válida. |
| Salidas | Grafo consultable por el servicio de enrutamiento. |
| Errores | Topología inválida: ver FR-01. |
| Criterios de aceptación | AC-02.1: Se obtienen rutas correctas en al menos dos topologías de estructura distinta (por ejemplo, lineal y en malla) sin modificar el código. AC-02.2: En un grafo desconectado, un par de nodos de componentes distintos produce PATH\_NOT\_FOUND. |
| Pruebas / verificación | Casos de prueba de topologías de referencia y grafos desconectados; identificadores por confirmar en 06-test-specification.md. |

### 4.4 FR-03 · Cálculo de rutas con Dijkstra

| Campo | Detalle |
| :---- | :---- |
| Aplicación | Controller. |
| Descripción | El Controller debe calcular el camino de costo mínimo entre origen y destino con el algoritmo de Dijkstra, considerando únicamente enlaces operativos y utilizables y costos no negativos. |
| Entradas | Nodo origen, nodo destino y métrica. |
| Salidas | Lista ordenada de nodos del camino y costo total. |
| Errores | NODE\_NOT\_FOUND y PATH\_NOT\_FOUND. |
| Criterios de aceptación | AC-03.1: En una topología de referencia con camino mínimo único conocido, el camino y el costo coinciden con los valores esperados. AC-03.2: Si origen y destino son el mismo nodo existente, el camino contiene solo ese nodo y el costo es 0\. AC-03.3: El cálculo reside en RoutingService, no en los manejadores HTTP. |
| Pruebas / verificación | Pruebas unitarias de rutas y costos; revisión arquitectónica. Los identificadores TC deben confirmarse en 06-test-specification.md. |

### 4.5 FR-04 · Métricas de costo: retardo, ancho de banda inverso y pérdida

| Campo | Detalle |
| :---- | :---- |
| Aplicación | Controller. |
| Descripción | El Controller debe soportar delay, bandwidth y loss con las definiciones de la sección 4.1. Los enlaces con p \= 1 son inutilizables y se excluyen del cálculo. |
| Entradas | Métrica delay, bandwidth o loss; por defecto, delay. |
| Salidas | Costo total igual a la suma de los costos de los enlaces de la ruta. |
| Errores | Métrica no soportada: 400 INVALID\_INPUT. |
| Criterios de aceptación | AC-04.1: Con delay, el costo total es la suma de los retardos del camino. AC-04.2: Con bandwidth, el costo total es la suma de 1/b de cada enlace. AC-04.3: Para loss, exp(-costo\_total) coincide con el producto de (1-p) de los enlaces de la ruta, con tolerancia de 1e-9. AC-04.4: Un enlace con p \= 1 nunca aparece en una ruta. AC-04.5: En la topología de referencia, al menos un par origen-destino produce caminos distintos según la métrica. |
| Pruebas / verificación | Pruebas unitarias y de integración para las tres métricas; identificadores TC por confirmar en 06-test-specification.md. |

### 4.6 FR-05 · API REST documentada para consultas del Controller

| Campo | Detalle |
| :---- | :---- |
| Aplicación | Controller. |
| Descripción | El Controller debe exponer GET /route, GET /topology, POST /links/fail, POST /links/restore y GET /health, documentados en 04-api-contract.md. Este requisito cubre las consultas (/route, /topology y /health); las operaciones de falla y restauración se cubren en FR-06. |
| Entradas | GET /route con src y dst obligatorios y metric opcional. |
| Salidas | JSON con path, metric, total\_cost y topology\_version para /route; topología vigente con el estado de cada enlace para /topology; respuesta de salud para /health. |
| Errores | 400 INVALID\_INPUT, 404 NODE\_NOT\_FOUND, 404 PATH\_NOT\_FOUND y 500 INTERNAL\_ERROR, según el endpoint y la condición. |
| Criterios de aceptación | AC-05.1: Una consulta válida a /route responde 200 con path, metric, total\_cost y topology\_version. AC-05.2: /topology responde 200 con la topología vigente, el estado de cada enlace y la versión. AC-05.3: /health responde 200 cuando el Controller está activo. AC-05.4: Los estados y formatos coinciden con 04-api-contract.md. |
| Pruebas / verificación | Pruebas de contrato para todos los endpoints y estados; identificadores TC por confirmar en 06-test-specification.md. |

### 4.7 FR-06 · Simulación de falla y restauración de enlaces

| Campo | Detalle |
| :---- | :---- |
| Aplicación | Controller. |
| Descripción | El Controller debe permitir deshabilitar y restaurar un enlace existente, identificado por sus dos extremos, mediante POST /links/fail y POST /links/restore. Las rutas posteriores deben reflejar el nuevo estado. El archivo de topología no se modifica. |
| Entradas | Extremos del enlace. |
| Salidas | Confirmación de la operación y topology\_version vigente. La versión aumenta en cada cambio efectivo. |
| Errores | 400 INVALID\_INPUT y 404 LINK\_NOT\_FOUND. |
| Criterios de aceptación | AC-06.1: Tras fallar un enlace de la ruta vigente, una nueva consulta no lo incluye y devuelve una ruta alternativa, si existe, o PATH\_NOT\_FOUND. AC-06.2: Tras restaurar un enlace previamente fallado, vuelve a ser elegible para el cálculo, salvo que tenga p \= 1\. En una topología de prueba donde la ruta original sea el único camino mínimo, la nueva consulta devuelve dicha ruta; si hay varios caminos mínimos equivalentes, se acepta cualquiera. AC-06.3: La versión aumenta en cada cambio efectivo. AC-06.4: Fallar un enlace ya fallado o restaurar uno ya activo responde 200 sin cambiar la versión. AC-06.5: El archivo JSON de topología no se modifica al fallar o restaurar enlaces. |
| Pruebas / verificación | Pruebas de falla, restauración, idempotencia y versión; identificadores TC por confirmar en 06-test-specification.md. |

### 4.8 FR-07 · Solicitud de rutas del Router al Controller por HTTP

| Campo | Detalle |
| :---- | :---- |
| Aplicación | Router. |
| Descripción | El Router debe obtener cada ruta consultando al Controller por HTTP. No debe calcular rutas por sí mismo. La dirección base del Controller y el tiempo de espera son configurables. |
| Entradas | Paquete con origen, destino y métrica. |
| Salidas | Ruta recibida del Controller y utilizada para el reenvío, tras validar que la respuesta cumple el contrato. |
| Errores | Ver FR-09. |
| Criterios de aceptación | AC-07.1: Por cada paquete válido se emite exactamente una consulta GET /route al Controller. AC-07.2: El código del Router no contiene el algoritmo de Dijkstra ni usa NetworkX para calcular rutas. AC-07.3: La ruta reenviada coincide con la ruta válida devuelta por el Controller. |
| Pruebas / verificación | Pruebas de integración y revisión arquitectónica; identificadores TC por confirmar en 06-test-specification.md. |

### 4.9 FR-08 · Simulación de reenvío de paquetes

| Campo | Detalle |
| :---- | :---- |
| Aplicación | Router. |
| Descripción | El Router debe exponer POST /packets y simular el reenvío salto a salto siguiendo exactamente la ruta válida seleccionada por el Controller. |
| Entradas | Paquete con src y dst obligatorios, y packet\_id y metric opcionales. |
| Salidas | Resultado con packet\_id, status, path, trace, metric, total\_cost y topology\_version, según corresponda al resultado. Los campos no disponibles para una operación fallida pueden ser nulos conforme al contrato de API. |
| Errores | 400 INVALID\_INPUT por formato inválido; los demás errores se gestionan según FR-09. |
| Criterios de aceptación | AC-08.1: Los nodos de la traza coinciden, en orden, con la ruta del Controller, desde el origen hasta el destino. AC-08.2: Si la traza se completa, el estado es DELIVERED. AC-08.3: Si origen y destino coinciden, la traza contiene un solo nodo y el estado es DELIVERED. AC-08.4: La lógica de reenvío reside en ForwardingService, no en los manejadores HTTP. |
| Pruebas / verificación | Pruebas unitarias con cliente y DAO falsos, y pruebas de integración; identificadores TC por confirmar en 06-test-specification.md. |

### 4.10 FR-09 · Manejo de nodos inválidos, destinos inalcanzables y fallas de comunicación

| Campo | Detalle |
| :---- | :---- |
| Aplicación | Controller y Router. |
| Descripción | Ambas aplicaciones deben tratar de forma controlada los nodos inválidos, los destinos inalcanzables y los fallos de comunicación con el Controller, devolviendo los errores del catálogo de la sección 2.6. El Router debe distinguir errores de transporte, respuestas inválidas y errores de aplicación válidos. No debe intentar calcular una ruta localmente cuando el Controller no esté disponible o devuelva una respuesta inválida. |
| Clasificación de errores | Error de transporte: conexión rechazada, timeout u otro fallo de comunicación; se transforma en 503 CONTROLLER\_UNAVAILABLE. Respuesta inválida o incompatible: JSON mal formado, respuesta HTTP exitosa con campos obligatorios ausentes o tipos incompatibles, o contenido que no cumple el esquema de GET /route; se transforma en 503 CONTROLLER\_UNAVAILABLE. Error de aplicación válido: respuesta de error cuyo estado HTTP y código de aplicación corresponden al catálogo y a 04-api-contract.md; el Router conserva su significado, por ejemplo 404 NODE\_NOT\_FOUND o 404 PATH\_NOT\_FOUND. Error interno inesperado: se responde 500 INTERNAL\_ERROR, sin exponer trazas de pila ni detalles internos. |
| Entradas | Solicitud que produzca una de las condiciones anteriores. |
| Salidas | Respuesta JSON con código de aplicación y mensaje; en el Router, resultado registrado con estado INVALID\_NODE, NO\_ROUTE o CONTROLLER\_UNAVAILABLE para los errores de reenvío correspondientes. |
| Errores | 400, 404, 500 y 503, según el catálogo y el contrato. |
| Criterios de aceptación | AC-09.1: Un nodo inexistente produce 404 NODE\_NOT\_FOUND. AC-09.2: Un destino inalcanzable produce 404 PATH\_NOT\_FOUND, distinguible de AC-09.1 por el código de aplicación. AC-09.3: Con el Controller detenido, el Router responde 503 CONTROLLER\_UNAVAILABLE cuando la persistencia del resultado se completa correctamente y sigue activo. AC-09.4: Un error inesperado produce 500 INTERNAL\_ERROR sin exponer trazas internas y la aplicación sigue activa. AC-09.5: Un fallo de conexión o timeout al consultar el Controller produce 503 CONTROLLER\_UNAVAILABLE. AC-09.6: Una respuesta del Controller con JSON mal formado o incompatible con el esquema de ruta produce 503 CONTROLLER\_UNAVAILABLE. AC-09.7: Un error de aplicación válido devuelto por el Controller conserva su código y significado conforme a 04-api-contract.md; no se transforma en 503 únicamente por tener un estado HTTP de error. |
| Pruebas / verificación | Pruebas de errores de aplicación, transporte, respuesta inválida y continuidad del Router; identificadores TC por confirmar en 06-test-specification.md. |

### 4.11 FR-10 · Registro de resultados de reenvío mediante DAO

| Campo | Detalle |
| :---- | :---- |
| Aplicación | Router. |
| Descripción | El Router debe registrar los resultados de reenvío a través de la interfaz ForwardingLogDAO, que encapsula el almacenamiento y la recuperación de ForwardingResult. Se intenta registrar un resultado por cada paquete bien formado, incluidos los fallidos. Las solicitudes mal formadas no generan registro.Manejo de excepciones internas inesperadas: Cuando ocurra una excepción interna inesperada durante el procesamiento de una solicitud que haya superado la validación local, el Router deberá: Conservar o generar un packet\_id para identificar la operación. Devolver una respuesta HTTP 500 Internal Server Error, utilizando el esquema de errores definido en el contrato de API. Intentar registrar el resultado de la operación con el estado INTERNAL\_ERROR. Registrar la excepción en los logs técnicos, sin exponer trazas internas ni información sensible al cliente. No clasificar como DELIVERED una operación que no haya finalizado correctamente. Si la persistencia del resultado falla, el Router deberá registrar también el fallo de almacenamiento y no afirmar que la operación quedó persistida. Criterios de aceptación adicionales: Una excepción inesperada después de la validación local produce una respuesta HTTP 500 con el código INTERNAL\_ERROR. La operación se identifica mediante packet\_id cuando esté disponible. El Router intenta persistir el resultado con estado INTERNAL\_ERROR. Un fallo de persistencia queda diferenciado del error original. La respuesta no contiene información interna sensible. |
| Entradas | Resultado de reenvío de un paquete bien formado. |
| Salidas | Resultado almacenado y recuperable mediante el DAO cuando la operación de persistencia termina correctamente. |
| Errores | Si falla el almacenamiento mediante ForwardingLogDAO, el Router devuelve 500 INTERNAL\_ERROR con un mensaje estable que no exponga detalles internos y permanece activo. No debe afirmar que el resultado quedó almacenado si la operación falló. El resultado de la simulación y el resultado de su persistencia deben distinguirse internamente. |
| Criterios de aceptación | AC-10.1: Tras un reenvío exitoso y una persistencia correcta, el DAO contiene un registro con packet\_id, status y path. AC-10.2: Los reenvíos fallidos se registran con el estado correspondiente si la persistencia funciona. AC-10.3: ForwardingService puede probarse con un ForwardingLogDAO falso en memoria, sin servidor HTTP ni archivos. AC-10.4: Las solicitudes con formato inválido no generan registro. AC-10.5: Si ForwardingLogDAO falla al almacenar un resultado, el Router responde 500 INTERNAL\_ERROR, no reporta el registro como persistido y permanece operativo para solicitudes posteriores. |
| Pruebas / verificación | Pruebas unitarias con DAO falso y prueba de fallo de persistencia; los identificadores TC deben formalizarse en 06-test-specification.md. |

---

## 5\. Requisitos no funcionales

NFR-01 a NFR-09 expresan las restricciones de calidad del enunciado, precisadas con criterios verificables. NFR-10 y NFR-11 son requisitos medibles adicionales aprobados por ambos integrantes el 27 de octubre de 2026. Sus umbrales forman parte de la línea base; la conformidad solo podrá declararse después de ejecutar y documentar las pruebas correspondientes.



| ID | Requisito | Método de verificación | Criterio de aceptación |
| :---- | :---- | :---- | :---- |
| NFR-01 | Ambas aplicaciones implementan MVC con responsabilidades documentadas: Modelo (objetos de dominio), Vista (esquemas de entrada y salida de la API), Controlador (manejadores HTTP que coordinan servicios) y servicios de dominio para la lógica de negocio. | Revisión de 02-static-architecture.md y del código; prueba de arquitectura. | Cada aplicación tiene módulos separados para modelo, vista, controlador y servicios. Ningún manejador contiene lógica de enrutamiento o reenvío. |
| NFR-02 | La carga, recuperación y persistencia de datos usan abstracciones DAO. Los servicios de dominio no acceden directamente al almacenamiento. | Prueba de arquitectura sobre las dependencias de los servicios; revisión de código. | Ningún servicio ni manejador realiza operaciones de archivo ni depende de una implementación concreta de DAO; dependen de interfaces. |
| NFR-03 | El algoritmo de Dijkstra y la lógica de reenvío permanecen fuera de los manejadores HTTP. | Revisión de código y prueba de arquitectura. | Dijkstra solo existe en RoutingService y el reenvío solo en ForwardingService; los manejadores validan, delegan y responden. |
| NFR-04 | Las interfaces HTTP/JSON coinciden con el contrato de API aprobado. | Pruebas de contrato sobre estados y campos de cada endpoint. | El 100 % de los endpoints del contrato tiene al menos una prueba que valida estado y campos. Todo cambio del contrato se registra. |
| NFR-05 | Los puertos, el archivo de topología y los demás parámetros de la sección 2.5 son configurables. | Ejecución con valores distintos de los predeterminados. | Ambas aplicaciones arrancan con otros puertos y otro archivo de topología sin modificar el código fuente. |
| NFR-06 | Los fallos esperados producen errores controlados y documentados, y las aplicaciones siguen activas. Esta tolerancia durante la ejecución no obliga a iniciar una aplicación con configuración inválida. Los errores fatales de inicialización —como ausencia del archivo de topología, JSON mal formado o topología que incumpla las reglas— impiden el inicio del Controller y producen un código de salida distinto de cero, conforme a FR-01. Una vez iniciadas, las aplicaciones deben manejar de forma controlada los errores de solicitudes, rutas inexistentes, enlaces no encontrados y fallas de comunicación, sin terminar el proceso. | Pruebas de cada error del catálogo y consulta posterior a /health. | Cada error esperado devuelve el estado y formato documentados. Después del error, /health responde 200 si la aplicación inició correctamente y continúa ejecutándose. |
| NFR-07 | La implementación es orientada a objetos y modular, con dependencias inyectables y sustituibles en pruebas. | Revisión de código; pruebas unitarias con dependencias sustitutas. | Ningún servicio crea internamente sus DAOs ni su cliente HTTP; recibe las dependencias por constructor. |
| NFR-08 | Cada requisito se vincula con tareas, componentes de código y pruebas automatizadas o revisiones verificables. | Revisión cruzada de los documentos 02, 05 y 06 frente a este documento. | El 100 % de los FR y NFR tiene al menos una tarea, un componente y una prueba o revisión asociada. Los identificadores deben existir en los documentos correspondientes. |
| NFR-09 | Los DAOs pueden sustituirse por mocks o fakes durante las pruebas. | Ejecución de pruebas unitarias de servicios con DAOs falsos. | Las pruebas de RoutingService y ForwardingService pueden ejecutarse sin depender de archivos reales; las pruebas unitarias no requieren levantar servidores HTTP. |
| NFR-10 | Rendimiento del Controller: una consulta GET /route debe responder en un máximo de 200 ms en el percentil 95, sobre una topología sintética conectada de 50 nodos y al menos 150 enlaces, con el Controller en la misma máquina que el cliente. Umbral aprobado por ambos integrantes el 27 de octubre de 2026. | Prueba automatizada que mide 100 consultas consecutivas por métrica con reloj monotónico; el p95 se calcula mediante nearest-rank (muestra ordenada de rango ceil(0,95 × n)); resultados registrados en test-results.txt. | Con una topología sintética conectada de al menos 50 nodos y 150 enlaces, se ejecutan 100 consultas válidas a GET /route por métrica (delay, bandwidth y loss). Se mide la latencia HTTP completa, desde el envío de la petición hasta la recepción completa de la respuesta. El percentil 95 debe ser \<= 200 ms para cada métrica. Se documentan topología, parámetros y condiciones para reproducir la prueba. Se usa nearest-rank: con 100 muestras ordenadas, el p95 es la muestra de rango 95. Si se realizan consultas de calentamiento, se ejecutan antes y no cuentan dentro de las 100 muestras de cada métrica. |
| NFR-11 | Resiliencia del Router ante la caída del Controller: con el Controller detenido, el Router debe responder a POST /packets con 503 CONTROLLER\_UNAVAILABLE en 3 s o menos (timeout predeterminado de 2 s más 1 s de margen) y mantenerse activo. Umbral aprobado por ambos integrantes el 27 de octubre de 2026. | Prueba de integración con 10 intentos consecutivos y demostración en vivo. | Los 10 intentos responden con 503 CONTROLLER\_UNAVAILABLE en \<= 3 s, siempre que el registro de cada resultado se persista correctamente. /health del Router responde 200\. Tras reiniciar el Controller, el siguiente paquete se procesa sin reiniciar el Router. Un fallo de persistencia del registro se clasifica como 500 INTERNAL\_ERROR, conforme a FR-10. |

---

## 6\. Matriz de trazabilidad

Esta matriz relaciona cada requisito funcional y no funcional con sus casos de uso, componentes responsables, tareas de implementación, responsables del equipo y pruebas o revisiones para verificar su cumplimiento.

Los nombres de componentes deben corresponder a 02-static-architecture.md. Las tareas se vinculan con los IMP definitivos de 05-implementation-plan.md; los casos detallados se identifican como TX y los casos TC-01 a TC-09 conservan el significado del PDF en 06-test-specification.md.

| Requisito | Casos de uso | Componentes principales | Tarea de implementación en 05 | Responsable | Verificación prevista |
| :---- | :---- | :---- | :---- | :---- | :---- |
| FR-01 | UC-01, UC-05 | TopologyDAO, FileTopologyDAO, Topology, RoutingService | IMP-04, IMP-05, IMP-09, IMP-19 | Controller — Andrés Felipe Mateus | TX-01–TX-08, TX-34; TC-08 |
| FR-02 | UC-01 | Topology, Link, RoutingService | IMP-09, IMP-10, IMP-19 | Controller — Andrés Felipe Mateus | TX-09–TX-10; TC-01, TC-08 |
| FR-03 | UC-01 | RoutingService | IMP-10, IMP-12, IMP-19, IMP-20 | Controller — Andrés Felipe Mateus | TX-11–TX-12; TC-01 |
| FR-04 | UC-01 | Link, RoutingService, estrategias de costo | IMP-05, IMP-10, IMP-19 | Controller — Andrés Felipe Mateus | TX-13–TX-17; TC-02 |
| FR-05 | UC-01, UC-05, UC-06 | Controladores API de ruta, topología y salud | IMP-12, IMP-13, IMP-20 | Controller — Andrés Felipe Mateus | TX-18–TX-24, TX-35; pruebas de contrato |
| FR-06 | UC-03, UC-04 | LinkManagementService, TopologyDAO, LinkAPIController | IMP-09, IMP-11, IMP-12, IMP-21 | Controller — Andrés Felipe Mateus | TX-25–TX-33, TX-63–TX-65; TC-03, TC-04 |
| FR-07 | UC-02 | ControllerClient, HttpControllerClient, ForwardingService | IMP-14, IMP-15, IMP-21, IMP-22 | Router — Santiago Cavarro | TX-39–TX-49, TX-57–TX-58; TC-05, TC-07 |
| FR-08 | UC-02 | ForwardingService, Packet, ForwardingResult | IMP-06, IMP-15, IMP-17, IMP-21 | Router — Santiago Cavarro | TX-37–TX-40, TX-62–TX-65; TC-05, TC-06 |
| FR-09 | UC-01, UC-02, UC-07 | Controladores API, RoutingService, ControllerClient | IMP-07, IMP-12, IMP-14, IMP-17, IMP-20, IMP-21 | Ambos | TX-23–TX-24, TX-35, TX-41–TX-49, TX-57, TX-69; TC-07 |
| FR-10 | UC-02, UC-07 | ForwardingService, ForwardingLogDAO, FileForwardingLogDAO | IMP-06, IMP-08, IMP-16, IMP-17, IMP-19, IMP-21 | Router — Santiago Cavarro | TX-50–TX-55, TX-69; TC-09 |
| NFR-01 | Todos | Controladores, vistas/esquemas, modelos y servicios de ambas aplicaciones | IMP-22, IMP-24 | Ambos | TX-34, TX-60 y revisión de código |
| NFR-02 | Todos | TopologyDAO, ForwardingLogDAO y sus implementaciones | IMP-08, IMP-16, IMP-19, IMP-22 | Ambos | TX-34, TX-52, TX-60 |
| NFR-03 | UC-01, UC-02 | RoutingService, ForwardingService | IMP-10, IMP-15, IMP-22 | Ambos | TX-34, TX-40, TX-60 |
| NFR-04 | Todos | Controladores API y esquemas de entrada/salida | IMP-12, IMP-17, IMP-20, IMP-25 | Ambos | TX-18–TX-30, TX-35, TX-37–TX-49, TX-69 |
| NFR-05 | UC-06 | Configuración y composición de Controller y Router | IMP-03, IMP-13, IMP-18, IMP-21 | Ambos | TX-36, TX-59 |
| NFR-06 | UC-06, UC-07 | Controladores, servicios y adaptadores | IMP-07, IMP-12, IMP-14, IMP-17, IMP-21 | Ambos | TX-02–TX-03, TX-35, TX-45–TX-49, TX-53, TX-56–TX-58 |
| NFR-07 | Todos | Modelos, servicios, interfaces y adaptadores | IMP-08, IMP-22 | Ambos | TX-34, TX-52, TX-60 |
| NFR-08 | Todos | Matriz de trazabilidad, plan de implementación y especificación de pruebas | IMP-19, IMP-20, IMP-21, IMP-25 | Ambos | Matriz de trazabilidad de 06; revisión cruzada |
| NFR-09 | Todos | Interfaces DAO y ControllerClient | IMP-08, IMP-19, IMP-22 | Ambos | TX-34, TX-52, TX-60 |
| NFR-10 | UC-01 | RoutingService, API del Controller y topología de prueba | IMP-23 | Controller — Andrés Felipe Mateus | Protocolo NFR-10 de 06; 100 muestras por métrica |
| NFR-11 | UC-07 | ControllerClient, ForwardingService, endpoint de salud del Router | IMP-23 | Router — Santiago Cavarro | TX-57, TX-66–TX-67 |

### 6.1 Reglas para mantener la trazabilidad

1. Cada requisito FR y NFR debe tener al menos una tarea identificada en 05-implementation-plan.md y un componente o conjunto de componentes identificable en 02-static-architecture.md.  
2. Cada requisito debe estar asociado a una prueba automatizada o a una revisión documental con criterios de aceptación verificables.  
3. Las pruebas deben comprobar el comportamiento especificado; no basta con verificar que existan clases, archivos o endpoints.  
4. Los casos detallados se identifican como TX-01 a TX-69; los casos TC-01 a TC-09 conservan el significado fijado por el PDF del taller y se vinculan con los TX que los implementan.  
5. La prueba de fallo de persistencia del DAO debe formalizarse si se mantiene AC-10.5 como criterio obligatorio.  
6. Los cambios en un requisito deben reflejarse en los componentes, tareas y pruebas relacionados.  
7. La matriz de especificación se considera trazable cuando no existan identificadores huérfanos ni referencias a pruebas inexistentes; la evidencia de ejecución se registra por separado.

---

## 7\. Criterios de aceptación globales

El sistema se considera aceptado cuando se cumplan todas las condiciones siguientes:

1. Cada FR y NFR está implementado y verificado, o su estado incompleto está documentado explícitamente. No se deben modificar los requisitos para acomodarlos a un comportamiento incorrecto del código.  
2. Existen pruebas automatizadas aprobadas para los requisitos funcionales y no funcionales verificables. La cantidad mínima de pruebas se establecerá en 06-test-specification.md; deben incluirse pruebas de RoutingService con TopologyDAO falso, de ForwardingService con ControllerClient y ForwardingLogDAO falsos, y de manejo de errores.  
3. La revisión del código confirma que ningún manejador HTTP contiene algoritmos de enrutamiento o lógica de reenvío y que el Router no calcula rutas.  
4. La demostración en vivo muestra ambos procesos independientes y, como mínimo:  
   1. Reenvío de un paquete.  
   2. Falla de un enlace de la ruta y obtención de una ruta alternativa o resultado inalcanzable.  
   3. Restauración del enlace y verificación del estado actualizado.  
   4. Una prueba con dependencias DAO sustitutas.  
   5. Manejo de la indisponibilidad del Controller y recuperación posterior del Router.  
5. Los requisitos, diagramas, contrato de API, plan de implementación y casos de prueba son consistentes entre sí, y ambos integrantes confirman la línea base.  
6. Los resultados de las pruebas y, cuando corresponda, las mediciones de rendimiento se conservan en los artefactos definidos por el plan de pruebas.

---

## 8\. Control de cambios y aprobación

### 8.1 Registro de versiones

| Versión | Fecha | Descripción | Autores |
| :---- | :---- | :---- | :---- |
| 1.0 | 20 de octubre de 2026 | Versión inicial para revisión cruzada y congelamiento. | A. F. Mateus, S. Cavarro |
| 1.1 | 20 de octubre de 2026 | Reorganización y corrección de consistencia; clarificación de errores, estado/versionado de topología, persistencia y trazabilidad. | A. F. Mateus, S. Cavarro |
| 1.2 | 27 de octubre de 2026 | Cierre de INTERNAL_ERROR, configuración y umbrales aprobados, trazabilidad TX/TC y correcciones editoriales. | A. F. Mateus, S. Cavarro |

### 8.2 Registro de cambios posteriores al congelamiento

Todo cambio posterior al congelamiento debe registrar su motivo y los artefactos afectados, y requiere la aprobación de ambos integrantes.

| ID | Fecha | Motivo | Artefactos afectados | Aprobado |
| :---- | :---- | :---- | :---- | :---- |
| CH-02 | 27 de octubre de 2026 | INTERNAL_ERROR es estado de ForwardingStatus y excepción interna diferenciada de persistencia. | 01, 02, 03, 04, 05, 06 | Aprobado, 27 de octubre de 2026 — ambos integrantes |
| CH-03 | 27 de octubre de 2026 | Aprobación de configuración por variables de entorno, timeout, reintentos, umbrales NFR-10/NFR-11 y método nearest-rank para p95. | 01, 04, 05, 06 | Aprobado, 27 de octubre de 2026 — ambos integrantes |
| CH-04 | 27 de octubre de 2026 | IDs TX para casos detallados y TC-01 a TC-09 reservados al significado del PDF; trazabilidad sincronizada. | 01, 03, 04, 05, 06 | Aprobado, 27 de octubre de 2026 — ambos integrantes |
| CH-05 | 27 de octubre de 2026 | Correcciones editoriales, nombres canónicos y registros de aprobación/versiones. | 01, 02, 03, 04, 05, 06 | Aprobado, 27 de octubre de 2026 |

### 8.3 Aprobación de la línea base

| Integrante | Rol | Confirmación | Fecha |
| :---- | :---- | :---- | :---- |
| Andrés Felipe Mateus | Controller | Aprobado, 27 de octubre de 2026 | 27 de octubre de 2026 |
| Santiago Cavarro | Router | Aprobado, 27 de octubre de 2026 | 27 de octubre de 2026 |

---

Estado del documento: versión 1.2, línea base aprobada el 27 de octubre de 2026. La aprobación de la línea base no implica que las pruebas hayan sido ejecutadas.




