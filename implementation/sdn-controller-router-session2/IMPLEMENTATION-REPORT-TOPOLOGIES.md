# NetLab SDN — Ampliación de la aplicación de Sesión 2

## Alcance

Se conserva la arquitectura Controller–Router, la topología T1 como estado inicial y los seis documentos aprobados. Esta entrega amplía la misma aplicación de Sesión 2; no constituye una sesión académica nueva.

## Cambios

- Se agregaron cinco topologías JSON seleccionables desde la interfaz: 6, 8, 11, 13 y 16 routers.
- Cada escenario tiene 10, 13, 21, 24 y 31 enlaces, respectivamente.
- Cada topología ofrece un par recomendado N01 → último nodo con tres rutas distintas según la métrica `delay`, `bandwidth` y `loss`.
- Los nodos incluyen ciudades y coordenadas geográficas ilustrativas para el mapa.
- Se añadió catálogo desplegable en la barra de herramientas. La selección carga el JSON y lo importa en el Controller; los controles existentes (inspección, fallos/restauración, exportación y simulación de paquetes) operan sobre la topología activa.
- Se corrigió la normalización de nodos al importar topologías.
- La selección de extremos ahora es explícita: primero se activa “Seleccionar emisor” o “Seleccionar destinatario” y luego se hace clic en el router. Un clic sin modo activo solo abre el inspector.
- Se añadió `docs/TOPOLOGY-CATALOG.md` con las topologías y el flujo de interacción.

## Criterios de enrutamiento

El Controller usa Dijkstra sobre costos aditivos:
- `delay`: suma de `delay_ms`.
- `bandwidth`: suma de `1 / bandwidth_mbps` (heurística aditiva; no representa el cuello de botella extremo a extremo).
- `loss`: suma de `-ln(1 - loss_probability)`, equivalente a minimizar la pérdida acumulada bajo independencia de enlaces.

Los cinco JSON fueron comprobados para que las tres métricas produzcan caminos diferentes para el par recomendado.

## Verificación ejecutada

- `python -m pytest -q`: **30 passed**.
- `node --check web/app.js`: sintaxis JavaScript válida.
- Prueba HTTP con Controller y Router levantados como procesos separados: health de ambos OK; importación de topología de 16 routers/31 enlaces; envío de paquetes entregados para `delay`, `bandwidth` y `loss`; cada uno siguió el camino esperado y distinto.
- Tras la prueba HTTP, `data/topology.json` fue restaurado a T1 de cuatro nodos para que el proyecto arranque con la línea base aprobada.

## Ejecución

Mantener dos terminales:

```bash
python -m controller.run
python -m router.run
```

Abrir `http://127.0.0.1:8001/`. En la barra superior, seleccionar T1 o una de las cinco topologías. Para el experimento recomendado de cada JSON, usar N01 como emisor y el último nodo como destinatario.
