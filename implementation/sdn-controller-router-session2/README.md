# SDN Controller + Router — Sesión 2

Implementación educativa conforme a la línea base SDD de `specs/01` a `specs/06`. Son dos aplicaciones FastAPI independientes; el Controller es la única autoridad de rutas y el Router simula el reenvío y registra resultados. No transmite paquetes reales ni implementa OpenFlow.

## 1. Interfaz didáctica NetLab SDN

El Controller sirve una interfaz web en **http://127.0.0.1:8001/**. Inicie primero Controller y Router (sección 4) y abra esa dirección en el navegador. La interfaz incluye:

- Mapa geográfico interactivo OpenStreetMap con nodos, ciudades y enlaces; clic en un router para elegir emisor/destino y clic en un enlace para inspeccionar sus métricas.
- Importación y exportación de topologías JSON de tamaño variable, con validación de identificadores, enlaces y métricas. Los nodos pueden ser cadenas o registros `{ "id", "city", "lat", "lon", "description" }`.
- Posiciones geográficas explícitas por nodo; para nodos sin coordenadas se generan posiciones ilustrativas. La importación se persiste en `data/topology.json`.
- Simulación extremo a extremo a través del Router (`POST /packets`), con la ruta devuelta por el Controller resaltada, costo, saltos y explicación del algoritmo.
- Experimentos para interrumpir y restaurar enlaces, más un módulo de conceptos SDN.

El mapa usa teselas de OpenStreetMap y Leaflet desde CDN, por lo que requiere conexión a Internet para cargar el mapa base. Sin coordenadas, la posición es ilustrativa y no representa una ciudad real. La interfaz se sirve desde el Controller; el Router permite CORS únicamente desde los orígenes locales `localhost:8001` y `127.0.0.1:8001`.

### Formato de importación

```json
{
  "nodes": [
    {"id": "R1", "city": "Bogotá", "lat": 4.711, "lon": -74.0721},
    {"id": "R2", "city": "Cali", "lat": 3.4516, "lon": -76.532}
  ],
  "links": [
    {"node_a": "R1", "node_b": "R2", "delay_ms": 5, "bandwidth_mbps": 100, "loss_probability": 0.01}
  ]
}
```

Los enlaces son bidireccionales. Cada enlace requiere retardo no negativo, ancho de banda mayor que cero y probabilidad de pérdida entre 0 y 1. Los identificadores de nodo deben ser únicos; no se permiten bucles ni enlaces duplicados.

## 2. Línea base y discrepancia documental

`data/topology.json` contiene la topología T1 de cuatro nodos y cuatro enlaces definida en los seis documentos aprobados de la Sesión 1. El PDF del equipo también incluye un ejercicio diferente de seis nodos (A–F, nueve enlaces); esa topología **no** reemplaza T1. La decisión y la comparación de métricas se registran en [`docs/discrepancy-log.md`](docs/discrepancy-log.md). Los seis documentos aprobados se conservan sin cambios.

## 3. Requisitos

- Python 3.11 o superior.
- Las dependencias de `requirements.txt`.
- Ejecutar los comandos desde la raíz del repositorio.

## 4. Instalación

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
```

## 5. Iniciar las aplicaciones

Abra dos terminales, ambas ubicadas en la raíz del repositorio.

Terminal 1 — Controller:

```bash
python -m controller.run
```

Terminal 2 — Router:

```bash
python -m router.run
```

Documentación interactiva: http://127.0.0.1:8001/docs y http://127.0.0.1:8002/docs.

### Variables de entorno

| Variable | Predeterminado | Uso |
|---|---|---|
| `CONTROLLER_HOST` | `127.0.0.1` | Host de escucha Controller. |
| `CONTROLLER_PORT` | `8001` | Puerto Controller. |
| `ROUTER_HOST` | `127.0.0.1` | Host de escucha Router. |
| `ROUTER_PORT` | `8002` | Puerto Router. |
| `TOPOLOGY_FILE_PATH` | `data/topology.json` | Archivo de topología inicial. |
| `CONTROLLER_BASE_URL` | `http://127.0.0.1:8001` | URL base que consume el Router. |
| `CONTROLLER_TIMEOUT_SECONDS` | `2` | Timeout de la llamada Router→Controller; no hay reintentos. |
| `FORWARDING_LOG_PATH` | `logs/forwarding.jsonl` | Registro JSONL del Router. |
| `LOG_LEVEL` | `INFO` | Nivel de log. |

Los entrypoints `python -m controller.run` y `python -m router.run` leen host y puerto de las variables de entorno. Si se invoca Uvicorn directamente, los argumentos `--host` y `--port` controlan la escucha. Si el Router usa otro host/puerto de Controller, actualice `CONTROLLER_BASE_URL`.

## 6. Prueba rápida de extremo a extremo

Con ambos procesos en ejecución:

```bash
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:8002/health
curl "http://127.0.0.1:8001/route?src=A&dst=D&metric=delay"
curl -X POST http://127.0.0.1:8002/packets -H "Content-Type: application/json" -d '{"packet_id":"demo-001","src":"A","dst":"D","metric":"delay"}'
curl -X POST http://127.0.0.1:8001/links/fail -H "Content-Type: application/json" -d '{"node_a":"B","node_b":"D"}'
curl -X POST http://127.0.0.1:8002/packets -H "Content-Type: application/json" -d '{"packet_id":"demo-002","src":"A","dst":"D","metric":"delay"}'
curl -X POST http://127.0.0.1:8001/links/restore -H "Content-Type: application/json" -d '{"node_a":"B","node_b":"D"}'
```

Resultado esperado en la topología inicial: `A-B-D`, costo de retardo `20`. Con `B-D` fallado, la siguiente consulta usa `A-C-D`, costo `35`. Restaurar `B-D` vuelve a habilitar la ruta inicial. La versión aumenta solo cuando cambia efectivamente el estado de un enlace.

## 7. Topología y persistencia

- `data/topology.json` define nodos y atributos de enlaces. El Controller valida el archivo al arrancar; un archivo ausente o inválido impide el inicio.
- Todos los enlaces comienzan activos y la versión inicia en `1`. Los cambios de estado son solo en memoria; reiniciar Controller restaura el estado inicial del JSON.
- `logs/forwarding.jsonl` se crea cuando se guarda el primer resultado. Cada línea es un objeto JSON independiente.
- Un paquete inválido no consulta al Controller ni genera registro. Los fallos posteriores a la validación local intentan registrar el resultado. Si falla la escritura, la API devuelve `500 INTERNAL_ERROR` sin afirmar que el registro quedó almacenado.

## 8. Pruebas automatizadas

```bash
pytest -q
```

Los tests cubren rutas/métricas, fallos y restauración, idempotencia, distinción entre nodo inexistente y camino ausente, uso de dobles DAO/cliente, errores de API y límites arquitectónicos. TC-08 y TC-09 se ejecutan sin servidor HTTP, con dobles de prueba.

Para ejecutar también las verificaciones reproducibles de NFR-10 (100 muestras por métrica sobre un grafo sintético de 50 nodos/150 enlaces) y NFR-11 (10 respuestas durante la caída del Controller y comprobación de recuperación), use `python scripts/verify_nfr.py`. El script genera `nfr-results.json` con las muestras individuales, p95 nearest-rank y tiempos de resiliencia del entorno donde se ejecutó. Los resultados de esta máquina no sustituyen la repetición en el equipo de presentación.

Para guardar la salida real de la ejecución:

```bash
pytest -q | tee test-results.txt
```

No se debe editar el resultado para ocultar fallos. Si se modifica el código o las pruebas, volver a ejecutar el comando y conservar la salida de esa ejecución.

## 9. Estructura del proyecto

- `controller/`: modelos, métricas, DAO de topología, servicios de dominio y controladores HTTP.
- `web/`: interfaz didáctica NetLab SDN (HTML, CSS y JavaScript).
- `router/`: modelos de paquete/resultado, cliente HTTP, servicio de forwarding, DAO JSONL y controladores HTTP.
- `tests/`: pruebas unitarias, integración API y arquitectura.
- `specs/`: seis documentos aprobados de la sesión 1, copiados sin alterar su contenido.
- `docs/NETLAB-USER-GUIDE.md`: guía de importación y uso de la interfaz.
- `IMPLEMENTATION-REPORT-SESSION3.md`: informe de esta evolución.
- `docs/discrepancy-log.md`: registro de la discrepancia entre T1 y el ejercicio A–F del PDF del equipo.
- `demo-evidence/http-integration-results.json`: resultado estructurado de la integración HTTP ejecutada para esta entrega.
- `prompts-session1.md` y `prompts-session2.md`: registro de prompting y revisión crítica.

## 10. Limitaciones conocidas

- Simulación a nivel de aplicación, no OpenFlow ni tráfico de red real.
- Sin autenticación, autorización ni base de datos. La interfaz gráfica es una SPA ligera servida por el Controller.
- Estado de enlaces y topología importada persistidos en `data/topology.json`; el estado operativo de enlaces se reinicia activo al importar/arrancar.
- La métrica `bandwidth` suma `1/b` por enlace; es una heurística aditiva y no maximiza el ancho de banda mínimo del camino.
- El mapa geográfico usa Leaflet/OpenStreetMap y requiere Internet para las teselas; la lógica de simulación permanece en los servicios locales.
- La entrega incluye tests automatizados, pero la evidencia de ejecución y las capturas de la demostración deben generarse en el equipo que presenta el taller.

## 11. Abrir y ejecutar en PyCharm

1. Descomprima el ZIP y abra la carpeta raíz `sdn-controller-router-session2` como proyecto existente.
2. En **Settings/Preferences → Project → Python Interpreter**, cree un entorno virtual con Python 3.11+.
3. Instale las dependencias desde la terminal de PyCharm: `python -m pip install -r requirements.txt`.
4. Cree dos configuraciones **Python** con el directorio de trabajo en la raíz del proyecto: módulo `controller.run` y módulo `router.run`. Ejecute primero Controller y después Router. Mantenga los puertos predeterminados 8001 y 8002, salvo que ajuste también `CONTROLLER_BASE_URL`.
5. Para pruebas, cree una configuración de tipo **Python tests → pytest** apuntando al directorio `tests`, o ejecute `python -m pytest -q` desde la terminal.
6. `data/topology.json` se resuelve respecto al directorio de trabajo; asegúrese de que ambas configuraciones usen la raíz del proyecto.

## 12. Evidencia para la entrega

Antes de entregar:

1. Ejecutar los tests y guardar `test-results.txt` con la salida real.
2. Capturar ambos `/health`, una entrega normal, la ruta tras fallar un enlace y la ruta tras restaurarlo.
3. Mostrar al menos un test con DAO falso en el que no se levante un servidor HTTP.
4. Completar `prompts-session1.md` y `prompts-session2.md` con las salidas/observaciones reales del equipo.
5. Ambos integrantes deben poder explicar las dos aplicaciones, el contrato, la inyección de dependencias y los fallos controlados.

## Catálogo de topologías para prácticas

En la barra superior de NetLab SDN puedes seleccionar T1 o cualquiera de las cinco topologías didácticas incluidas en `web/topologies/`. El catálogo crece de 6 a 16 routers. Cada JSON incluye coordenadas ilustrativas, enlaces, métricas y un experimento recomendado entre `N01` y el último nodo. Para ese par, las rutas esperadas son distintas al optimizar por retardo, ancho de banda (costo aditivo 1/Mbps) o pérdida (costo aditivo −ln(1−p)). También puedes importar JSON propios o exportar la topología activa.

### Selección explícita de extremos

Pulsa **Seleccionar emisor** y luego el router deseado en el mapa. Después pulsa **Seleccionar destinatario** y elige otro router. Cuando ninguno de esos modos está activo, hacer clic sobre un router únicamente abre su inspector; nunca cambia accidentalmente los extremos.
