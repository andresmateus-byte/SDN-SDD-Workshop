# Informe de implementación — NetLab SDN (Sesión 3)

## Objetivo

Evolucionar el proyecto SDN Controller + Router a una herramienta didáctica con interfaz gráfica, mapa geográfico, exploración de routers/enlaces, importación de topologías arbitrarias y simulación visual de rutas, manteniendo la arquitectura previa y T1 como topología inicial.

## Funcionalidades implementadas

- Interfaz web en español servida por el Controller en `/` y recursos estáticos en `/static`.
- Mapa Leaflet/OpenStreetMap; marcadores de routers con ciudad y coordenadas, enlaces seleccionables y estados activos/caídos.
- T1 aparece con ubicaciones de demostración: A–Popayán, B–Cali, C–Pasto, D–Bogotá. Son ubicaciones pedagógicas, no afirmaciones sobre despliegue físico.
- Importación JSON y exportación JSON desde la interfaz.
- Importación acepta nodos como cadenas o como objetos `{id, city, lat, lon, description}`.
- Validación de identificadores únicos, extremos existentes, ausencia de autoenlaces/duplicados, retardo no negativo, ancho de banda positivo y pérdida en [0,1].
- La topología importada se persiste en el archivo configurado por `TOPOLOGY_FILE_PATH`; el cambio aumenta la versión de topología.
- Selección de emisor/destino haciendo clic en los routers.
- Simulación extremo a extremo usando `POST /packets` del Router; el Controller sigue siendo autoridad de cálculo. Se resalta el camino, se muestran costo, saltos, versión y explicación.
- Inspector contextual de routers y enlaces; controles de interrupción/restauración.
- Sección de aprendizaje con explicación de plano de control/datos, métricas y algoritmo.
- CORS limitado al origen local de la interfaz para comunicación entre los puertos 8001 y 8002.

## Pruebas ejecutadas

- `python -m pytest -q`: **29 passed**.
- `node --check web/app.js`: sintaxis JavaScript correcta.
- Prueba HTTP real con procesos independientes: `/` respondió 200; `/health` de Controller y Router respondieron 200; `POST /packets` entregó el paquete de prueba `ui-e2e-1` por `A-B-D`, costo 20.0 y versión 1.
- Pruebas de interfaz/servido de recursos: `/`, `/static/app.js`.
- Prueba de importación de topología de tres routers georreferenciados: importación 200, ruta R1-R2-R3 costo 9.0; topología inválida con identificadores duplicados rechazada con 400.

## Archivos principales añadidos/modificados

- `web/index.html`, `web/style.css`, `web/app.js`
- `controller/app.py`
- `controller/controllers/topology_controller.py`
- `controller/dao/file_topology_dao.py`
- `router/app.py`
- `tests/integration/test_educational_interface.py`
- `docs/NETLAB-USER-GUIDE.md`

## Decisiones y límites

- Se conserva T1 como ejemplo inicial y se conservan los seis documentos SDD aprobados.
- La interfaz requiere conexión a Internet para cargar Leaflet y teselas OpenStreetMap. Los nodos importados sin coordenadas reciben posiciones ilustrativas; no son ciudades reales.
- La persistencia usa un JSON local. Es apropiada para una práctica de un usuario; no resuelve transacciones multiusuario ni edición concurrente.
- El criterio de ancho de banda conserva la heurística preexistente `sum(1/b)`, no equivale a maximizar el mínimo ancho de banda extremo a extremo.
- La aplicación continúa siendo una simulación a nivel de aplicación. No es un controlador OpenFlow ni configura equipos físicos.

## Cómo iniciar

En dos terminales desde la raíz del proyecto: `python -m controller.run` y `python -m router.run`. Abrir `http://127.0.0.1:8001/`. La guía completa está en `docs/NETLAB-USER-GUIDE.md`.
