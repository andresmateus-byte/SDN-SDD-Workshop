# 04 — Contrato de API

| Campo | Detalle |
| :---- | :---- |
| Proyecto | Solución educativa tipo SDN: Controller y Router (REST/JSON) |
| Documento | specs/04-api-contract.md |
| Versión del contrato | 1.2 — línea base aprobada |
| Fecha | 27 de octubre de 2026 |
| Estado | Línea base aprobada |
| Documentos base | 01-requirements.md v1.2, 02-static-architecture.md v1.2 y 03-dynamic-architecture.md v1.2 |
| Controller (Estudiante A) | Andrés Felipe Mateus |
| Router (Estudiante B) | Santiago Ramirez Chavarro |

1\. Introducción

### 1.1 Propósito

Este documento es el contrato único entre los dos procesos y entre el sistema y sus clientes. Define cada endpoint, su método HTTP, los parámetros, los esquemas JSON de entrada y salida, los códigos de estado y los errores. También formaliza la estructura del archivo de topología descrita en 01-requirements.md, sección 2.4. Es la referencia de NFR-04: las interfaces implementadas deben coincidir con este contrato. No contiene código de implementación.

### 1.2 Relación con los demás documentos

| Documento | Relación |
| :---- | :---- |
| 01-requirements | Fuente de los códigos de estado y de aplicación (catálogo 2.6), de las métricas (4.1) y de las reglas de validación de la topología (2.4). |
| 02-static-architecture | Los esquemas JSON de la sección 7 corresponden a las clases de la capa Vista (secciones 6.2 y 6.4 de 02). |
| 03-dynamic-architecture | Cada interacción HTTP de los diagramas de secuencia aparece en las secciones 4 a 6\. |
| 06-test-specification.md | Los casos de contrato CT-01 en adelante de la sección 10 deben mapearse explícitamente a los casos de prueba TC definidos en el documento 06; los prefijos CT y TC no son intercambiables. |

### 1.3 Decisiones cerradas y ajustes a documentos previos

02-static-architecture.md (sección 11.2) y 03-dynamic-architecture.md (sección 9.3) identifican decisiones que este contrato propone cerrar:

| Punto | Resolución |
| :---- | :---- |
| Nombres definitivos de los campos JSON | Los de las secciones 4, 5 y 7 de este documento (notación snake\_case). |
| ¿El cuerpo de error del Router incluye packet\_id? | Sí. En las respuestas de error posteriores a la validación local de un paquete bien formado se incluye packet\_id, incluso si el resultado no pudo persistirse; en el 400 de validación local se omite porque no se acepta ni registra el paquete (A-07). |
| Forma de ForwardingResultResponse si el estado no es DELIVERED | ForwardingResultResponse solo se devuelve con estado DELIVERED (200). Los demás estados se devuelven como ErrorResponse (sección 5.2). |
| Error interno inesperado después de validar un paquete | La API responde HTTP `500 INTERNAL_ERROR` e incluye el `packet_id` cuando la solicitud superó la validación local. El Router intenta crear y persistir un `ForwardingResult` con estado `INTERNAL_ERROR`, siempre que disponga de la información necesaria. Si falla la persistencia, no afirma que el resultado quedó almacenado. |

**Nomenclatura canónica de componentes**

Los nombres de componentes deben coincidir con `02-static-architecture.md` y `03-dynamic-architecture.md`:

* `TopologyDAO`: interfaz de acceso a la topología.  
* `FileTopologyDAO`: implementación de producción de `TopologyDAO`.  
* `LinkManagementService`: servicio responsable de fallar y restaurar enlaces.  
* `TopologyQueryService`: servicio responsable de consultar la topología.  
* `RouterHealthAPIController`: controlador HTTP de salud del Router.  
* `HealthAPIController`: controlador HTTP de salud del Controller.

Las referencias a `FileTopologyDAO`, `TopologyQueryService` o `HealthAPIController (Router)` que se utilicen como nombres de componentes deben sustituirse por los nombres canónicos correspondientes. Los nombres de endpoints, requisitos y casos de prueba no deben modificarse por esta normalización.

## 2\. Convenciones generales

| Aspecto | Convención |
| :---- | :---- |
| Transporte | HTTP/1.1 sobre TCP. Sin cifrado ni autenticación (fuera del alcance). |
| Direcciones | `http://<host>:<controller_port>` y `http://<host>:<router_port>`. Los valores predeterminados aprobados son `8001` para el Controller y `8002` para el Router. Ambos puertos son configurables conforme a NFR-05. |
| Formato | JSON en UTF-8. Toda respuesta, incluidos los errores, lleva Content-Type: application/json. Los cuerpos de solicitud llevan el mismo tipo de contenido. |
| Nombres de campos | snake\_case. |
| Identificadores de nodo | Cadena de texto no vacía y no compuesta solo por espacios. Distingue mayúsculas y minúsculas. |
| Métrica | delay, bandwidth o loss, en minúsculas. Es opcional y por defecto vale delay. |
| Números | total\_cost, delay\_ms, bandwidth\_mbps y loss\_probability son números JSON. Un valor entero puede serializarse como 20 o 20.0; el cliente debe tratarlo como número. |
| Versión de topología | Entero mayor o igual que 1\. Comienza en 1 y aumenta solo con una falla o restauración efectiva. |
| Validación | Todo error de validación de entrada produce 400 INVALID\_INPUT. El sistema nunca devuelve 422\. |
| Campos desconocidos | En las solicitudes se ignoran. Las respuestas contienen exactamente los campos definidos. |
| Rutas o métodos no definidos | Fuera del contrato: responde el framework (404 o 405\) y el cliente no debe depender de esa respuesta. |
| Idempotencia | GET no modifica estado. POST /links/fail y POST /links/restore son idempotentes (A-05). POST /packets no es idempotente: cada solicitud bien formada genera un intento de procesamiento y un registro del resultado cuando la persistencia está disponible. Si falla la escritura del registro, se devuelve 500 INTERNAL\_ERROR; no se debe afirmar que el resultado quedó persistido. |

## 3\. Modelo de errores

Todo error se devuelve con el mismo formato:

```json
{
  "error": "PATH_NOT_FOUND",
  "message": "No existe un camino entre 'A' y 'D' con los enlaces activos."
}
```

error es el código de aplicación (estable y apto para pruebas automáticas) y message es un texto legible en español (informativo, no apto para lógica de cliente). En el Router, el objeto incluye además packet\_id cuando se indica en la sección 5.2.

### 3.1 Catálogo de errores

| Código de aplicación | HTTP | Condición | Aplicación |
| :---- | :---- | :---- | :---- |
| INVALID\_INPUT | 400 | Parámetro o campo ausente, vacío o mal formado; métrica no soportada; cuerpo que no es JSON válido. | Controller y Router |
| NODE\_NOT\_FOUND | 404 | El nodo origen o destino no existe en la topología. | Controller y Router |
| LINK\_NOT\_FOUND | 404 | No existe un enlace entre los dos nodos indicados (incluye el caso de nodos inexistentes o extremos iguales). | Controller |
| PATH\_NOT\_FOUND | 404 | Ambos nodos existen pero no hay camino con los enlaces usables. | Controller y Router |
| CONTROLLER\_UNAVAILABLE | 503 | El Router no puede obtener una respuesta válida del Controller. | Router |
| INTERNAL\_ERROR | 500 | Error inesperado o fallo del registro de reenvíos. El mensaje es genérico y no expone detalles internos. | Controller y Router |

### 3.2 Nodo inválido frente a camino ausente

Ambos errores comparten el estado 404, pero se distinguen siempre por el campo error: NODE\_NOT\_FOUND: el origen o el destino no pertenece a la topología. PATH\_NOT\_FOUND: ambos nodos existen, pero no están conectados por enlaces usables (por ejemplo, tras fallar enlaces). La entrada mal formada (ausente, vacía, métrica desconocida) es una categoría distinta: 400 INVALID\_INPUT.

### 3.3 Orden de validación

Formato de la solicitud (JSON, parámetros, campos, métrica) → 400\. Existencia de los nodos (primero src, luego dst) → 404 NODE\_NOT\_FOUND. Existencia de un camino → 404 PATH\_NOT\_FOUND.

## 4\. API del Controller

### 4.1 GET /health

Informa que el Controller está disponible. Respuesta 200

```json
{
  "status": "ok",
  "application": "controller"
}
```

Errores: 500 INTERNAL\_ERROR únicamente ante un fallo interno inesperado. La falta de respuesta por proceso detenido no constituye una respuesta HTTP.

### 4.2 GET /topology

Devuelve la topología activa: nodos, enlaces con su estado y la versión vigente. Aspecto Detalle Parámetros Ninguno. Respuesta exitosa 200 TopologyResponse Errores 500 INTERNAL\_ERROR

Respuesta 200

```json
{
  "nodes": [
    "A",
    "B",
    "C",
    "D"
  ],
  "links": [
    {
      "node_a": "A",
      "node_b": "B",
      "delay_ms": 10,
      "bandwidth_mbps": 100,
      "loss_probability": 0.01,
      "active": true
    },
    {
      "node_a": "B",
      "node_b": "D",
      "delay_ms": 10,
      "bandwidth_mbps": 100,
      "loss_probability": 0.01,
      "active": true
    },
    {
      "node_a": "A",
      "node_b": "C",
      "delay_ms": 15,
      "bandwidth_mbps": 50,
      "loss_probability": 0.02,
      "active": true
    },
    {
      "node_a": "C",
      "node_b": "D",
      "delay_ms": 20,
      "bandwidth_mbps": 50,
      "loss_probability": 0.02,
      "active": true
    }
  ],
  "topology_version": 1
}
```

### 4.3 GET /route

Calcula y devuelve la ruta de menor costo entre dos nodos usando solo enlaces usables (activos y con pérdida menor que 1). Parámetros de consulta

| Parámetro | Tipo | Obligatorio | Descripción |
| :---- | :---- | :---- | :---- |
| src | Texto | Sí | Nodo origen. |
| dst | Texto | Sí | Nodo destino. |
| metric | Texto | No | delay (por defecto), bandwidth o loss. |

Respuestas

| Estado | Código de aplicación | Condición |
| :---- | :---- | :---- |
| 200 | — | Ruta encontrada (RouteResponse). |
| 400 | INVALID\_INPUT | Falta src o dst, un valor está vacío, o metric no es soportada. |
| 404 | NODE\_NOT\_FOUND | src o dst no existe. |
| 404 | PATH\_NOT\_FOUND | No hay camino entre dos nodos existentes. |
| 500 | INTERNAL\_ERROR | Error inesperado. |

Ejemplo: GET /route?src=A\&dst=D\&metric=delay → 200

```json
{
  "path": [
    "A",
    "B",
    "D"
  ],
  "metric": "delay",
  "total_cost": 20.0,
  "topology_version": 1
}
```

Ejemplo: GET /route?src=A\&dst=D\&metric=bandwidth → 200 (costo \= 1/100 \+ 1/100)

```json
{
  "path": [
    "A",
    "B",
    "D"
  ],
  "metric": "bandwidth",
  "total_cost": 0.02,
  "topology_version": 1
}
```

Ejemplo: GET /route?src=A\&dst=D\&metric=loss → 200 (costo \= −ln(1 − 0,01) × 2\)

```json
{
  "path": [
    "A",
    "B",
    "D"
  ],
  "metric": "loss",
  "total_cost": 0.020100672,
  "topology_version": 1
}
```

Ejemplo: GET /route?src=A\&dst=A → 200 (origen igual a destino: ruta de un nodo con costo 0\)

```json
{
  "path": [
    "A"
  ],
  "metric": "delay",
  "total_cost": 0.0,
  "topology_version": 1
}
```

Ejemplo: GET /route?src=A\&dst=Z → 404

```json
{
  "error": "NODE_NOT_FOUND",
  "message": "El nodo 'Z' no existe en la topología."
}
```

Ejemplo: GET /route?src=A\&dst=D con los enlaces B-D y C-D fallados → 404

```json
{
  "error": "PATH_NOT_FOUND",
  "message": "No existe un camino entre 'A' y 'D' con los enlaces activos."
}
```

Ejemplo: GET /route?src=A\&dst=D\&metric=speed → 400

```json
{
  "error": "INVALID_INPUT",
  "message": "La métrica 'speed' no es soportada. Valores válidos: delay, bandwidth, loss."
}
```

Notas Si existen varios caminos con el mismo costo mínimo, cualquiera es válido (A-09). topology\_version es la versión de la instantánea usada en el cálculo. Con metric=bandwidth, el costo es la suma de 1/b: es una heurística y no equivale a maximizar el ancho de banda del cuello de botella.

### 4.4 POST /links/fail

Deshabilita un enlace existente. Las consultas de ruta posteriores lo excluyen. Cuerpo de la solicitud (LinkChangeRequest)

```json
{
  "node_a": "B",
  "node_b": "D"
}
```

Los extremos no tienen orden: B-D y D-B identifican el mismo enlace. Respuestas

| Estado | Código de aplicación | Condición |
| :---- | :---- | :---- |
| 200 | — | Operación aplicada o ya aplicada (LinkChangeResponse). |
| 400 | INVALID\_INPUT | Cuerpo ausente o no JSON; node\_a o node\_b ausentes, vacíos o que no son texto. |
| 404 | LINK\_NOT\_FOUND | No existe un enlace entre esos nodos. |
| 500 | INTERNAL\_ERROR | Error inesperado. |

Ejemplo: primera solicitud → 200

```json
{
  "node_a": "B",
  "node_b": "D",
  "active": false,
  "changed": true,
  "topology_version": 2
}
```

Ejemplo: repetir la misma solicitud → 200 (idempotente: changed es false y la versión no cambia)

```json
{
  "node_a": "B",
  "node_b": "D",
  "active": false,
  "changed": false,
  "topology_version": 2
}
```

Ejemplo: enlace inexistente → 404

```json
{
  "error": "LINK_NOT_FOUND",
  "message": "No existe un enlace entre 'A' y 'D'."
}
```

### 4.5 POST /links/restore

Rehabilita un enlace existente. Usa el mismo cuerpo de solicitud, los mismos errores y las mismas reglas de idempotencia que POST /links/fail. Ejemplo: → 200

```json
{
  "node_a": "B",
  "node_b": "D",
  "active": true,
  "changed": true,
  "topology_version": 3
}
```

Un enlace con loss\_probability igual a 1 puede restaurarse (queda activo), pero sigue sin ser utilizable en el cálculo de rutas (A-02).

## 5\. API del Router

### Configuración base y control de cambios

Configuración aprobada el 27 de octubre de 2026: puertos predeterminados 8001 (Controller) y 8002 (Router), timeout de 2 segundos, un único intento sin reintentos automáticos, `data/topology.json` para la topología y `logs/forwarding.jsonl` para el registro. Los parámetros se configuran mediante variables de entorno y todos son sobrescribibles.

La aplicación debe permitir cambiar los parámetros sin modificar el código fuente, conforme a NFR-05. Una vez aprobados, los valores predeterminados y sus nombres deben coincidir en `01-requirements.md`, `04-api-contract.md`, `05-implementation-plan.md` y `06-test-specification.md`. Toda modificación posterior debe registrarse en el control de cambios.

### 5.1 GET /health

Informa solo la disponibilidad del propio Router. No consulta al Controller (A-08), por lo que responde 200 aunque el Controller esté caído. Respuesta 200

```json
{
  "status": "ok",
  "application": "router"
}
```

Errores: 500 INTERNAL\_ERROR únicamente ante un fallo interno inesperado. La caída del Controller no es un error de este endpoint y no debe afectar su respuesta.

### 5.2 POST /packets

Recibe un paquete simulado, obtiene la ruta del Controller, simula el reenvío salto a salto y registra el resultado. Cuerpo de la solicitud (PacketRequest)

| Campo | Tipo | Obligatorio | Descripción |
| :---- | :---- | :---- | :---- |
| src | Texto | Sí | Nodo origen. |
| dst | Texto | Sí | Nodo destino. |
| packet\_id | Texto (1 a 64 caracteres, no solo espacios) | No | Identificador del paquete. Si falta, el Router genera uno no vacío. El contrato no garantiza unicidad global entre solicitudes. |
| metric | Texto | No | delay (por defecto), bandwidth o loss. El Router la valida antes de contactar al Controller (AD-10). |

Significado de packet\_id en errores: En las respuestas de error de POST /packets posteriores a la validación local, packet\_id identifica el paquete asociado al procesamiento cuando su valor ya se ha resuelto. Su presencia en la respuesta no garantiza que exista un resultado persistido. Si ocurre un error interno inesperado o falla la persistencia, el Router devuelve 500 INTERNAL\_ERROR sin afirmar que el resultado quedó guardado. Las solicitudes rechazadas con 400 INVALID\_INPUT no incluyen packet\_id ni generan un registro.

````json
{"packet_id":"pkt-001","status":"DELIVERED","src":"A","dst":"D","path":["A","B","D"],"trace":["A","B","D"],"metric":"delay","total_cost":20.0,"topology_version":1,"timestamp":"2026-10-20T15:04:05Z","message":null}

| HTTP | Código de aplicación | Condición | Estado ForwardingStatus que se intenta persistir | `packet_id` |
| :---- | :---- | :---- | :---- | :---- |
| 200 | — | Paquete entregado (`ForwardingResultResponse`). | `DELIVERED` | Sí |
| 400 | `INVALID_INPUT` | Cuerpo no JSON, `src`/`dst` ausentes o vacíos, `packet_id` inválido o métrica no soportada. | Ninguno; la solicitud no supera la validación local. | No |
| 404 | `NODE_NOT_FOUND` | El Controller informa que el origen o destino no existe. | `INVALID_NODE` | Sí |
| 404 | `PATH_NOT_FOUND` | El Controller informa que no hay camino utilizable. | `NO_ROUTE` | Sí |
| 503 | `CONTROLLER_UNAVAILABLE` | No se obtuvo una respuesta válida del Controller. | `CONTROLLER_UNAVAILABLE` | Sí |
| 500 | `INTERNAL_ERROR` | Excepción interna inesperada después de la validación local. | Se intenta persistir `INTERNAL_ERROR`; si el DAO falla, no se confirma el registro. | Sí, cuando ya se resolvió |
| 500 | `INTERNAL_ERROR` | Fallo de persistencia de un resultado ya calculado. | No se afirma que el resultado esté persistido; el fallo de almacenamiento se registra por separado. | Sí, cuando ya se resolvió |

En los errores 404, message conserva el mensaje de aplicación informado por el Controller. En cualquier error posterior a la validación local se incluye el packet\_id ya resuelto, incluso si falla la persistencia; las solicitudes rechazadas con 400 no incluyen packet\_id ni generan registro. Ejemplo: → 200

```json
{
  "packet_id": "pkt-001",
  "status": "DELIVERED",
  "path": [
    "A",
    "B",
    "D"
  ],
  "trace": [
    "A",
    "B",
    "D"
  ],
  "metric": "delay",
  "total_cost": 20.0,
  "topology_version": 1
}
````

path es la ruta devuelta por el Controller y trace es la lista ordenada de nodos recorridos en la simulación. En un reenvío entregado, ambas coinciden. Con origen igual a destino, ambas contienen un solo nodo. Ejemplo: tras fallar el enlace B-D → 200 con la ruta alterna

```json
{
  "packet_id": "pkt-002",
  "status": "DELIVERED",
  "path": [
    "A",
    "C",
    "D"
  ],
  "trace": [
    "A",
    "C",
    "D"
  ],
  "metric": "delay",
  "total_cost": 35.0,
  "topology_version": 2
}
```

Ejemplo: nodo inexistente → 404

```json
{
  "error": "NODE_NOT_FOUND",
  "message": "El nodo 'Z' no existe en la topología.",
  "packet_id": "pkt-003"
}
```

Ejemplo: sin camino → 404

```json
{
  "error": "PATH_NOT_FOUND",
  "message": "No existe un camino entre 'A' y 'D' con los enlaces activos.",
  "packet_id": "pkt-004"
}
```

Ejemplo: Controller no disponible → 503 (respuesta en 3 s o menos, NFR-11)

```json
{
  "error": "CONTROLLER_UNAVAILABLE",
  "message": "No fue posible obtener una respuesta válida del Controller.",
  "packet_id": "pkt-005"
}
```

Ejemplo: solicitud mal formada → 400 (sin packet\_id, no se registra)

```json
{
  "error": "INVALID_INPUT",
  "message": "El campo 'dst' es obligatorio."
}
```

## 6\. Interacción Router → Controller

El Router consulta al Controller exclusivamente con GET /route (sección 4.3), mediante HttpControllerClient. La política de la llamada es:

| Aspecto | Valor |
| :---- | :---- |
| Intentos | Uno solo, sin reintentos (A-10). |
| Tiempo de espera | controller\_timeout\_seconds (2 s por defecto). |
| Parámetros | src, dst y metric del paquete, ya validados por el Router. |

### 6.1 Traducción de las respuestas del Controller

| Respuesta del Controller | Excepción en el Router | Estado del resultado | Respuesta del Router |
| :---- | :---- | :---- | :---- |
| 200 con cuerpo válido según RouteResponse | — | DELIVERED (tras el reenvío) | 200 |
| 404 con error igual a NODE\_NOT\_FOUND | NodeNotFoundError | INVALID\_NODE | 404 NODE\_NOT\_FOUND |
| 404 con error igual a PATH\_NOT\_FOUND | PathNotFoundError | NO\_ROUTE | 404 PATH\_NOT\_FOUND |
| Conexión rechazada o inalcanzable | ControllerUnavailableError | CONTROLLER\_UNAVAILABLE | 503 |
| Tiempo de espera agotado | ControllerUnavailableError | CONTROLLER\_UNAVAILABLE | 503 |
| 5xx | ControllerUnavailableError | CONTROLLER\_UNAVAILABLE | 503 |
| 400 ante un paquete ya validado (AD-10) | ControllerUnavailableError | CONTROLLER\_UNAVAILABLE | 503 |
| 404 con otro código, o 200 con cuerpo inválido o campos faltantes | ControllerUnavailableError | CONTROLLER\_UNAVAILABLE | 503 |

## 7\. Esquemas JSON

Los esquemas siguen JSON Schema (borrador 2020-12). Los de respuesta no admiten campos adicionales: agregar un campo es un cambio de contrato (sección 12).

### 7.1 Controller

RouteResponse

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "RouteResponse",
  "type": "object",
  "required": [
    "path",
    "metric",
    "total_cost",
    "topology_version"
  ],
  "properties": {
    "path": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "string",
        "minLength": 1,
        "pattern": "\\S"
      }
    },
    "metric": {
      "enum": [
        "delay",
        "bandwidth",
        "loss"
      ]
    },
    "total_cost": {
      "type": "number",
      "minimum": 0
    },
    "topology_version": {
      "type": "integer",
      "minimum": 1
    }
  },
  "additionalProperties": false
}
```

TopologyResponse

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "TopologyResponse",
  "type": "object",
  "required": [
    "nodes",
    "links",
    "topology_version"
  ],
  "properties": {
    "nodes": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1,
        "pattern": "\\S"
      },
      "uniqueItems": true
    },
    "links": {
      "type": "array",
      "items": {
        "$ref": "#/$defs/LinkSchema"
      }
    },
    "topology_version": {
      "type": "integer",
      "minimum": 1
    }
  },
  "$defs": {
    "LinkSchema": {
      "type": "object",
      "required": [
        "node_a",
        "node_b",
        "delay_ms",
        "bandwidth_mbps",
        "loss_probability",
        "active"
      ],
      "properties": {
        "node_a": {
          "type": "string",
          "minLength": 1,
          "pattern": "\\S"
        },
        "node_b": {
          "type": "string",
          "minLength": 1,
          "pattern": "\\S"
        },
        "delay_ms": {
          "type": "number",
          "minimum": 0
        },
        "bandwidth_mbps": {
          "type": "number",
          "exclusiveMinimum": 0
        },
        "loss_probability": {
          "type": "number",
          "minimum": 0,
          "maximum": 1
        },
        "active": {
          "type": "boolean"
        }
      },
      "additionalProperties": false
    }
  },
  "additionalProperties": false
}
```

LinkChangeRequest

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "LinkChangeRequest",
  "type": "object",
  "required": [
    "node_a",
    "node_b"
  ],
  "properties": {
    "node_a": {
      "type": "string",
      "minLength": 1,
      "pattern": "\\S"
    },
    "node_b": {
      "type": "string",
      "minLength": 1,
      "pattern": "\\S"
    }
  }
}
```

LinkChangeResponse

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "LinkChangeResponse",
  "type": "object",
  "required": [
    "node_a",
    "node_b",
    "active",
    "changed",
    "topology_version"
  ],
  "properties": {
    "node_a": {
      "type": "string",
      "minLength": 1,
      "pattern": "\\S"
    },
    "node_b": {
      "type": "string",
      "minLength": 1,
      "pattern": "\\S"
    },
    "active": {
      "type": "boolean"
    },
    "changed": {
      "type": "boolean"
    },
    "topology_version": {
      "type": "integer",
      "minimum": 1
    }
  },
  "additionalProperties": false
}
```

ErrorResponse (Controller)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ErrorResponse (Controller)",
  "type": "object",
  "required": [
    "error",
    "message"
  ],
  "properties": {
    "error": {
      "enum": [
        "INVALID_INPUT",
        "NODE_NOT_FOUND",
        "LINK_NOT_FOUND",
        "PATH_NOT_FOUND",
        "INTERNAL_ERROR"
      ]
    },
    "message": {
      "type": "string",
      "minLength": 1
    }
  },
  "additionalProperties": false
}
```

### 7.2 Router

PacketRequest

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "PacketRequest",
  "type": "object",
  "required": [
    "src",
    "dst"
  ],
  "properties": {
    "packet_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 64,
      "pattern": "\\S"
    },
    "src": {
      "type": "string",
      "minLength": 1,
      "pattern": "\\S"
    },
    "dst": {
      "type": "string",
      "minLength": 1,
      "pattern": "\\S"
    },
    "metric": {
      "enum": [
        "delay",
        "bandwidth",
        "loss"
      ],
      "default": "delay"
    }
  }
}
```

ForwardingResultResponse

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ForwardingResultResponse",
  "type": "object",
  "required": [
    "packet_id",
    "status",
    "path",
    "trace",
    "metric",
    "total_cost",
    "topology_version"
  ],
  "properties": {
    "packet_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 64,
      "pattern": "\\S"
    },
    "status": {
      "const": "DELIVERED"
    },
    "path": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "string",
        "minLength": 1,
        "pattern": "\\S"
      }
    },
    "trace": {
      "type": "array",
      "minItems": 1,
      "items": {
        "type": "string",
        "minLength": 1,
        "pattern": "\\S"
      }
    },
    "metric": {
      "enum": [
        "delay",
        "bandwidth",
        "loss"
      ]
    },
    "total_cost": {
      "type": "number",
      "minimum": 0
    },
    "topology_version": {
      "type": "integer",
      "minimum": 1
    }
  },
  "additionalProperties": false
}
```

ErrorResponse (Router)

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "ErrorResponse (Router)",
  "type": "object",
  "required": [
    "error",
    "message"
  ],
  "properties": {
    "error": {
      "enum": [
        "INVALID_INPUT",
        "NODE_NOT_FOUND",
        "PATH_NOT_FOUND",
        "CONTROLLER_UNAVAILABLE",
        "INTERNAL_ERROR"
      ]
    },
    "message": {
      "type": "string",
      "minLength": 1
    },
    "packet_id": {
      "type": "string",
      "minLength": 1,
      "maxLength": 64,
      "pattern": "\\S"
    }
  },
  "additionalProperties": false
}
```

### 7.3 Común

HealthResponse

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "HealthResponse",
  "type": "object",
  "required": [
    "status",
    "application"
  ],
  "properties": {
    "status": {
      "const": "ok"
    },
    "application": {
      "enum": [
        "controller",
        "router"
      ]
    }
  },
  "additionalProperties": false
}
```

## 8\. Archivos de datos

### 8.1 Archivo de topología (entrada del Controller)

El DAO de topología definido en 02 (implementación JSON denominada FileTopologyDAO; confirmar la nomenclatura frente a 03, que actualmente usa FileTopologyDAO) lee topology\_file\_path. El archivo tiene una lista de nodos y una lista de enlaces; los enlaces no incluyen el campo active (todos inician activos y con versión 1).

```json
{
  "nodes": [
    "A",
    "B",
    "C",
    "D"
  ],
  "links": [
    {
      "node_a": "A",
      "node_b": "B",
      "delay_ms": 10,
      "bandwidth_mbps": 100,
      "loss_probability": 0.01
    },
    {
      "node_a": "B",
      "node_b": "D",
      "delay_ms": 10,
      "bandwidth_mbps": 100,
      "loss_probability": 0.01
    },
    {
      "node_a": "A",
      "node_b": "C",
      "delay_ms": 15,
      "bandwidth_mbps": 50,
      "loss_probability": 0.02
    },
    {
      "node_a": "C",
      "node_b": "D",
      "delay_ms": 20,
      "bandwidth_mbps": 50,
      "loss_probability": 0.02
    }
  ]
}
```

Reglas de validación (de 01-requirements, sección 2.4): Los identificadores de nodo son únicos y no vacíos. Cada enlace une dos nodos existentes y distintos (sin bucles) y no se repite entre el mismo par, en ningún sentido. delay\_ms mayor o igual que 0, bandwidth\_mbps mayor que 0 y loss\_probability entre 0 y 1\. Una lista de enlaces vacía es válida. Los campos desconocidos se ignoran.

La validación semántica del archivo, además de JSON Schema, debe comprobar que node\_a y node\_b existan en nodes, que sean distintos y que cada par de extremos aparezca una sola vez sin importar el orden. JSON Schema por sí solo no expresa estas relaciones entre elementos; FileTopologyDAO debe aplicarlas antes de iniciar el Controller. Si el archivo no existe, no es JSON válido o incumple una regla, FileTopologyDAO lanza TopologyLoadError con un mensaje que identifica el campo o el enlace afectado, y el Controller no inicia (código de salida distinto de cero). TopologyFile

```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "TopologyFile",
  "type": "object",
  "required": [
    "nodes",
    "links"
  ],
  "properties": {
    "nodes": {
      "type": "array",
      "items": {
        "type": "string",
        "minLength": 1,
        "pattern": "\\S"
      },
      "uniqueItems": true
    },
    "links": {
      "type": "array",
      "items": {
        "type": "object",
        "required": [
          "node_a",
          "node_b",
          "delay_ms",
          "bandwidth_mbps",
          "loss_probability"
        ],
        "properties": {
          "node_a": {
            "type": "string",
            "minLength": 1,
            "pattern": "\\S"
          },
          "node_b": {
            "type": "string",
            "minLength": 1,
            "pattern": "\\S"
          },
          "delay_ms": {
            "type": "number",
            "minimum": 0
          },
          "bandwidth_mbps": {
            "type": "number",
            "exclusiveMinimum": 0
          },
          "loss_probability": {
            "type": "number",
            "minimum": 0,
            "maximum": 1
          }
        }
      }
    }
  }
}
```

### 8.2 Registro de reenvíos (salida del Router)

FileForwardingLogDAO agrega una línea JSON por resultado a forwarding\_log\_path (formato JSON Lines). El archivo es de uso interno: no es parte de la API HTTP, pero su estructura se documenta para las pruebas y las evidencias.

```json
{
  "packet_id": "pkt-001",
  "status": "DELIVERED",
  "src": "A",
  "dst": "D",
  "path": [
    "A",
    "B",
    "D"
  ],
  "trace": [
    "A",
    "B",
    "D"
  ],
  "metric": "delay",
  "total_cost": 20.0,
  "topology_version": 1,
  "timestamp": "2026-10-20T15:04:05Z",
  "message": null
}
```

Registro adicional de ejemplo para una excepción interna inesperada (una línea JSON independiente):

```json
{"packet_id":"pkt-002","status":"INTERNAL_ERROR","src":"A","dst":"D","path":[],"trace":[],"metric":"delay","total_cost":null,"topology_version":1,"timestamp":"2026-10-27T12:00:00Z","message":"Error interno inesperado"}
```

El valor persistido `status=INTERNAL_ERROR` describe el resultado de procesamiento. La respuesta HTTP `500` con código de error `INTERNAL_ERROR` es un elemento del contrato HTTP distinto. Si falla la persistencia, no se afirma que este registro exista en el archivo.

| Campo | Descripción |
| :---- | :---- |
| status | DELIVERED, INVALID\_NODE, NO\_ROUTE, CONTROLLER\_UNAVAILABLE o INTERNAL\_ERROR. |
| path, trace | Listas vacías en los fallos esperados. |
| total\_cost, topology\_version, message | Nulos cuando no aplican. |
| timestamp | Fecha y hora UTC en formato ISO 8601, asignada por ForwardingService con el reloj inyectado. |

## 9\. Secuencia de demostración

Con la topología de ejemplo de la sección 8.1, esta secuencia cubre el comportamiento en vivo exigido por el taller:

| Paso | Solicitud | Resultado esperado |
| :---- | :---- | :---- |
| 1 | Router: POST /packets (A a D, delay) | 200, ruta A, B, D, costo 20, versión 1\. |
| 2 | Controller: POST /links/fail (B, D) | 200, changed=true, versión 2\. |
| 3 | Router: POST /packets (A a D, delay) | 200, ruta A, C, D, costo 35, versión 2\. |
| 4 | Controller: POST /links/fail (C, D) | 200, changed=true, versión 3\. |
| 5 | Router: POST /packets (A a D, delay) | 404 PATH\_NOT\_FOUND. |
| 6 | Controller: POST /links/restore (B, D) | 200, changed=true, versión 4\. |
| 7 | Router: POST /packets (A a D, delay) | 200, ruta A, B, D, costo 20, versión 4\. |
| 8 | Detener el Controller y enviar POST /packets | 503 CONTROLLER\_UNAVAILABLE en 3 s o menos. |
| 9 | Router: GET /health | 200: el Router sigue activo. |

## 10\. Casos de contrato

Cada caso CT es una comprobación del contrato que debe quedar vinculado a una o más pruebas automatizadas con identificadores TC en 06-test-specification.md. La prueba comprueba, según corresponda, estado HTTP, código de aplicación, campos obligatorios, tipos y efectos observables (por ejemplo, registro o cambio de versión).

### 10.1 Controller

| ID | Solicitud | Resultado esperado |
| :---- | :---- | :---- |
| CT-01 | GET /health | 200, status=ok, application=controller. |
| CT-02 | GET /topology | 200, nodes, links con active y topology\_version. |
| CT-03 | GET /route con delay | 200 con path, metric, total\_cost y topology\_version. |
| CT-04 | GET /route con bandwidth | 200, costo igual a la suma de 1/b. |
| CT-05 | GET /route con loss | 200, e elevado a −costo igual al producto de (1 − p), con tolerancia de 1e-9. |
| CT-06 | GET /route sin metric | 200, metric=delay. |
| CT-07 | GET /route con src igual a dst | 200, ruta de un nodo y costo 0\. |
| CT-08 | GET /route sin dst | 400 INVALID\_INPUT. |
| CT-09 | GET /route con metric=speed | 400 INVALID\_INPUT. |
| CT-10 | GET /route con un nodo inexistente | 404 NODE\_NOT\_FOUND. |
| CT-11 | GET /route entre nodos existentes sin camino | 404 PATH\_NOT\_FOUND (distinto de CT-10 por el código). |
| CT-12 | POST /links/fail de un enlace existente | 200, active=false, changed=true, versión incrementada. |
| CT-13 | Repetir CT-12 | 200, changed=false, misma versión. |
| CT-14 | POST /links/fail de un enlace inexistente | 404 LINK\_NOT\_FOUND. |
| CT-15 | POST /links/fail con cuerpo inválido | 400 INVALID\_INPUT. |
| CT-16 | POST /links/restore de un enlace fallado | 200, active=true, changed=true, versión incrementada. |
| CT-17 | POST /links/restore de un enlace inexistente | 404 LINK\_NOT\_FOUND. |

### 10.2 Router

| ID | Solicitud | Resultado esperado |
| :---- | :---- | :---- |
| CT-18 | GET /health | 200, status=ok, application=router. |
| CT-19 | POST /packets válido | 200, status=DELIVERED, trace igual a path. |
| CT-20 | POST /packets sin packet\_id | 200 con un packet\_id generado y no vacío. |
| CT-21 | POST /packets sin src | 400 INVALID\_INPUT, sin registro. |
| CT-22 | POST /packets con métrica inválida | 400 INVALID\_INPUT, sin consulta al Controller. |
| CT-23 | POST /packets con nodo inexistente | 404 NODE\_NOT\_FOUND con packet\_id. |
| CT-24 | POST /packets sin camino | 404 PATH\_NOT\_FOUND con packet\_id. |
| CT-25 | POST /packets con el Controller detenido | 503 CONTROLLER\_UNAVAILABLE en 3 s o menos; después, GET /health responde 200\. |
| CT-26 | POST /packets con un Controller que devuelve un cuerpo inválido | 503 CONTROLLER\_UNAVAILABLE. |
| CT-27 | GET /topology y validación de su esquema | 200; cada enlace contiene node\_a, node\_b, delay\_ms, bandwidth\_mbps, loss\_probability y active; topology\_version es entero \>= 1\. |
| CT-28 | Repetir POST /links/restore sobre un enlace ya activo | 200, changed=false y la misma topology\_version. |
| CT-29 | POST /links/restore con cuerpo inválido | 400 INVALID\_INPUT; la topología no cambia. |
| CT-30 | POST /packets con JSON mal formado | 400 INVALID\_INPUT; no se consulta al Controller ni se intenta registrar. |
| CT-31 | POST /packets válido cuando falla ForwardingLogDAO.save | 500 INTERNAL\_ERROR con packet\_id; no se afirma que el resultado quedó persistido. |
| CT-32 | POST /packets cuando el Controller devuelve un error no reconocido o una respuesta incompatible | 503 CONTROLLER\_UNAVAILABLE; se intenta registrar CONTROLLER\_UNAVAILABLE. |
| CT-33 | GET /route ante un error interno inesperado del Controller | 500 INTERNAL\_ERROR con ErrorResponse. |
| CT-34 | GET /topology ante un error interno inesperado del Controller | 500 INTERNAL\_ERROR con ErrorResponse. |
| CT-35 | POST /links/fail con extremos iguales o sin enlace entre ellos | 404 LINK\_NOT\_FOUND; la versión no cambia. |
| CT-36 | POST /packets con packet\_id vacío, compuesto solo por espacios o de más de 64 caracteres | 400 INVALID\_INPUT; no se consulta al Controller ni se intenta registrar. |
| CT-37 | POST /packets después de superar la validación local, cuando ForwardingService lanza una excepción interna inesperada | 500 INTERNAL\_ERROR con `packet_id`; se intenta persistir un `ForwardingResult` con `status=INTERNAL_ERROR`; no se exponen detalles internos. Distinto de CT-31, que verifica el fallo de persistencia. |

## 11\. Trazabilidad

| Endpoint | Requisitos | Clases (02) | Escenario (03) | Casos de contrato |
| :---- | :---- | :---- | :---- | :---- |
| GET /health (Controller) | FR-05 | HealthAPIController (Controller) | — | CT-01 |
| GET /topology | FR-01, FR-05 | TopologyAPIController, TopologyQueryService, TopologyDAO | — | CT-02, CT-27, CT-34 |
| GET /route | FR-03, FR-04, FR-05, FR-09 | RouteAPIController, RoutingService y modelo Link/estrategia de costo definida en 02 | 1, 2 | CT-03 a CT-11, CT-33 |
| POST /links/fail | FR-06, FR-09 | LinkAPIController, LinkManagementService, TopologyDAO | 2 | CT-12 a CT-15, CT-35 |
| POST /links/restore | FR-06, FR-09 | LinkAPIController, LinkManagementService, TopologyDAO | 2 | CT-16, CT-17, CT-28, CT-29 |
| GET /health (Router) | FR-09, NFR-06, NFR-11 | RouterHealthAPIController | 3 | CT-18 |
| POST /packets | FR-07, FR-08, FR-09, FR-10, NFR-11 | PacketAPIController, ForwardingService, ControllerClient, ForwardingLogDAO | 1, 3 | CT-19 a CT-26, CT-30 a CT-32, CT-36, CT-37 |

NFR-04 solo puede declararse cumplido cuando todas las comprobaciones de contrato definidas aquí estén vinculadas a pruebas ejecutables y sus resultados se hayan documentado en 06-test-specification.md, cubriendo todos los endpoints, estados y esquemas. CT-37 cubre específicamente la excepción interna inesperada en POST /packets; CT-31 cubre por separado el fallo de persistencia. La existencia de esta tabla no demuestra que las pruebas se hayan ejecutado.

**Aprobación de umbrales no funcionales**

NFR-10 (p95 de GET /route ≤ 200 ms en la carga definida) y NFR-11 (POST /packets responde en ≤ 3 s con el Controller caído, timeout de 2 s más margen de 1 s) están aprobados por ambos integrantes el 27 de octubre de 2026\. Cualquier modificación posterior exige control de cambios coordinado en 01, 03, 05 y 06\.

Los umbrales aprobados son criterios definitivos de aceptación; no se declarará conformidad hasta que las pruebas correspondientes se ejecuten y sus resultados se documenten.

## 12\. Decisiones de contrato

| ID | Decisión | Justificación |
| :---- | :---- | :---- |
| API-01 | Los campos usan snake\_case. | Coherencia con los nombres de atributos de las clases de la Vista (02). |
| API-02 | NODE\_NOT\_FOUND y PATH\_NOT\_FOUND comparten el estado 404 y se distinguen por error. | Cumple la distinción exigida por el taller y es coherente con A-01. |
| API-03 | Los extremos iguales o inexistentes en /links/\* producen LINK\_NOT\_FOUND. | No existe ningún enlace entre esos nodos; evita un segundo código de error. |
| API-04 | Todo error de validación es 400; nunca 422\. | Un único estado para entradas inválidas; el framework debe configurarse en consecuencia (AD-08). |
| API-05 | POST /links/\* devuelve 200 y es idempotente, con changed indicando si hubo cambio. | Coherente con A-05; permite repetir la operación en la demostración sin errores. |
| API-06 | ForwardingResultResponse se devuelve para DELIVERED; los estados fallidos se representan conforme a los esquemas de respuesta de error, manteniendo el ForwardingResult persistido independiente del ErrorResponse HTTP. | Hace que el estado HTTP y el cuerpo sean coherentes y simplifica a los clientes. |
| API-07 | packet\_id es opcional en ErrorResponse del Router. | Permite correlacionar un error con el registro sin exponer datos de un paquete no registrado. |
| API-08 | Los campos desconocidos de las solicitudes se ignoran; las respuestas no admiten campos adicionales. | Tolerancia en la entrada y precisión en la salida. |
| API-09 | El mensaje de error es informativo y el cliente solo debe depender de error y del estado HTTP. | Los textos pueden mejorar sin romper el contrato. |
| API-10 | Los puertos 8001 y 8002 son valores predeterminados aprobados y configurables. | NFR-05 exige que sean configurables. |

## 13\. Control de cambios y aprobación

Todo cambio posterior al congelamiento (nuevo endpoint, campo, estado o código de error) es un cambio de contrato: se registra con su motivo, se refleja en los casos de contrato y requiere la aprobación de ambos integrantes.

### 13.1 Registro de versiones

| Versión | Fecha | Descripción | Autores |
| :---- | :---- | :---- | :---- |
| 1.0 | 20 de octubre de 2026 | Versión inicial para revisión cruzada y congelamiento. | A. F. Mateus, S. Cavarro |
| 1.1 | 22 de octubre de 2026 | Aclaraciones de validación semántica de topología, consistencia de errores y revisión de esquemas/casos de contrato. | A. F. Mateus, S. Cavarro |
| 1.2 | 27 de octubre de 2026 | INTERNAL\_ERROR persistido, CT-37, configuración y umbrales aprobados, trazabilidad TX/TC. | A. F. Mateus, S. Cavarro |

### 13.2 Registro de cambios posteriores al congelamiento

| ID | Fecha | Motivo | Artefactos afectados | Aprobado |
| :---- | :---- | :---- | :---- | :---- |
| CH-01 | 22 de octubre de 2026 | Alinear las reglas de validación de topología, precisar la correlación packet\_id y ampliar las comprobaciones de contrato. | 04-api-contract.md, 02-static-architecture.md y 03-dynamic-architecture.md. | Aprobado, 27 de octubre de 2026 |
| CH-02 | 27 de octubre de 2026 | Se incorpora INTERNAL\_ERROR como estado persistido y se diferencia del HTTP 500 y del fallo de persistencia. | 01, 02, 03, 04, 05, 06 | Aprobado, 27 de octubre de 2026 — ambos integrantes |
| CH-03 | 27 de octubre de 2026 | Configuración por variables de entorno, timeout, un intento, umbrales NFR y método nearest-rank para p95 aprobados. | 01, 04, 05, 06 | Aprobado, 27 de octubre de 2026 — ambos integrantes |
| CH-04 | 27 de octubre de 2026 | CT-37 se define para excepción interna en POST /packets y se sincronizan referencias TX/TC. | 03, 04, 05, 06 | Aprobado, 27 de octubre de 2026 — ambos integrantes |
| CH-05 | 27 de octubre de 2026 | Correcciones editoriales y sincronización de nombres. | 01, 02, 03, 04, 05, 06 | Aprobado, 27 de octubre de 2026 |

### 13.3 Aprobación de la línea base

| Integrante | Rol | Confirmación | Fecha |
| :---- | :---- | :---- | :---- |
| Andrés Felipe Mateus | Controller | Aprobado, 27 de octubre de 2026 | 27 de octubre de 2026 |
| Santiago Ramirez Chavarro | Router | Aprobado, 27 de octubre de 2026 | 27 de octubre de 2026 |

### 13.4 Registro de revisión y aprobación del diseño preliminar

| Integrante | Responsabilidad | Estado de revisión | Fecha | Observaciones |
| :---- | :---- | :---- | :---- | :---- |
| Andrés Felipe Mateus | Controller | Aprobado, 27 de octubre de 2026 | 27 de octubre de 2026 | Línea base documental aprobada; pruebas no ejecutadas por esta aprobación. |
| Santiago Ramirez Chavarro | Router | Aprobado, 27 de octubre de 2026 | 27 de octubre de 2026 | Línea base documental aprobada; pruebas no ejecutadas por esta aprobación. |

Ambos integrantes aprobaron la línea base documental el 27 de octubre de 2026\. Esta aprobación no implica que las pruebas estén ejecutadas ni que se hayan obtenido resultados.
