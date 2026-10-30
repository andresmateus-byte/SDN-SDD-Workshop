# Catálogo de topologías de práctica

T1 permanece como línea base de cuatro nodos. Se agregan cinco escenarios seleccionables desde la barra superior:

| Topología | Routers | Enlaces | Par recomendado |
|---|---:|---:|---|
| 2 | 6 | 10 | N01 → N06 |
| 3 | 8 | 13 | N01 → N08 |
| 4 | 11 | 21 | N01 → N11 |
| 5 | 13 | 24 | N01 → N13 |
| 6 | 16 | 31 | N01 → N16 |

Cada escenario tiene tres corredores con perfiles de costo diferentes. Para el par recomendado, `delay` elige el corredor de menor suma de retardos, `bandwidth` minimiza la suma de inversos de capacidad y `loss` minimiza la suma de `-ln(1-p)`. Se añaden enlaces transversales para crear mallas y alternativas; sus métricas se han configurado para no invalidar las rutas de demostración.

Los nodos llevan ciudades y coordenadas geográficas ilustrativas. No representan despliegues reales. La importación sigue validando identificadores únicos, extremos existentes, enlaces no duplicados, retardos no negativos, ancho de banda positivo y pérdida entre 0 y 1.

## Flujo de selección de origen y destino

La interacción es deliberadamente explícita:
1. Pulsar **Seleccionar emisor** activa el modo de origen.
2. Hacer clic en un router asigna el emisor y desactiva el modo.
3. Pulsar **Seleccionar destinatario** activa el modo de destino.
4. Hacer clic en otro router asigna el destino.
5. Un clic sin modo activo abre únicamente el inspector del router.
