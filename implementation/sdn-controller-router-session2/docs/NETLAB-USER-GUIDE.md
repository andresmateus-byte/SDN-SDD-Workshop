# NetLab SDN — guía de uso

## Inicio

1. Instale Python 3.11+ y ejecute `python -m pip install -r requirements.txt`.
2. Abra dos terminales en la raíz del proyecto.
3. Terminal 1: `python -m controller.run`.
4. Terminal 2: `python -m router.run`.
5. Abra `http://127.0.0.1:8001/` en Chrome, Edge o Firefox.

## Construir e importar una red

Pulse **Importar topología** y seleccione un archivo JSON. El formato acepta `nodes` como lista de identificadores o como lista de objetos con `id`, `city`, `lat`, `lon` y `description`. `links` debe contener `node_a`, `node_b`, `delay_ms`, `bandwidth_mbps` y `loss_probability`.

Ejemplo:

```json
{
  "nodes": [
    {"id":"R1", "city":"Bogotá", "lat":4.711, "lon":-74.0721},
    {"id":"R2", "city":"Cali", "lat":3.4516, "lon":-76.532},
    {"id":"R3", "city":"Pasto", "lat":1.2136, "lon":-77.2811}
  ],
  "links": [
    {"node_a":"R1", "node_b":"R2", "delay_ms":5, "bandwidth_mbps":100, "loss_probability":0.01},
    {"node_a":"R2", "node_b":"R3", "delay_ms":8, "bandwidth_mbps":50, "loss_probability":0.02}
  ]
}
```

Las coordenadas son latitud/longitud WGS84. Si se omiten, la interfaz crea posiciones ilustrativas para que la red se pueda explorar; no deben interpretarse como geolocalización real. El mapa utiliza Leaflet y teselas OpenStreetMap, por lo que necesita Internet. La simulación y el cálculo de rutas se ejecutan en los servicios locales.

## Seleccionar una ruta

- Primer clic sobre un router: lo asigna como emisor.
- Segundo clic sobre otro router: lo asigna como destino.
- Seleccione el criterio (retardo, ancho de banda heurístico o pérdida) y pulse **Simular envío de paquete**.
- El Router consulta al Controller y el mapa resalta en verde el camino devuelto.
- Seleccione un enlace en el mapa para inspeccionar sus métricas.
- En Experimentos puede interrumpir o restaurar el enlace seleccionado y volver a simular.

Para seleccionar nuevamente los extremos, haga clic en otro router después de haber completado ambos extremos; el ciclo empieza otra vez con el emisor.

## Lectura de las métricas

- **Retardo:** suma de milisegundos por enlace.
- **Ancho de banda:** el motor actual suma `1/bandwidth_mbps` por enlace. Es una heurística aditiva didáctica, no una optimización del ancho de banda mínimo del camino.
- **Pérdida:** suma `-ln(1-p)`; representa el costo aditivo equivalente de la probabilidad de pérdida.

El algoritmo de ruta es Dijkstra sobre enlaces activos. El color rojo discontinuo representa enlaces interrumpidos; el verde grueso resalta la ruta calculada.

## Escalabilidad y límites

La cantidad de nodos y enlaces no está fijada en la interfaz; se valida el grafo completo al importar y se calcula ruta sobre NetworkX. Para redes grandes, la visualización de muchos marcadores y teselas puede requerir clustering, agregación y carga por regiones. La persistencia actual es un JSON local, adecuado para laboratorio y demostraciones, no para concurrencia multiusuario/producción. No hay autenticación, control de acceso ni edición simultánea. La aplicación es un simulador a nivel de aplicación: no configura switches físicos, no implementa OpenFlow y no transmite tráfico real.
