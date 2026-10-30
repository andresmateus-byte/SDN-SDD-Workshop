# Corrección del selector de topologías — Sesión 2

## Problema corregido
El selector de la interfaz apuntaba a nombres de archivo que no coincidían con los nombres reales del catálogo en `web/topologies/`. Por eso la carga por selector fallaba aunque la importación manual desde un JSON sí funcionara.

## Cambios
- Se corrigieron las cinco rutas del selector para que coincidan con los archivos reales `topologia_01_6_routers.json` a `topologia_05_16_routers.json`.
- Se ajustaron las etiquetas para identificar las cinco topologías adicionales y sus tamaños.
- La sustitución de topología ahora se mantiene en memoria durante la ejecución; no sobrescribe `data/topology.json`.
- Se añadieron pruebas para verificar las rutas del catálogo y que la importación no altere el archivo base.
- Se conservaron las topologías de demostración, sus experimentos recomendados y las rutas diferenciadas por métrica incluidas en los JSON.

## Verificación
- `python -m pytest -q`: 31 pruebas aprobadas.
- Comprobación HTTP de los cinco JSON servidos desde `/static/topologies/`: 5/5 correctos.
- Comprobación de la topología base T1: conserva los cuatro routers y cuatro enlaces aprobados.

## Ubicación
- Topología base inmutable: `data/topology.json`.
- Catálogo seleccionable: `web/topologies/`.
