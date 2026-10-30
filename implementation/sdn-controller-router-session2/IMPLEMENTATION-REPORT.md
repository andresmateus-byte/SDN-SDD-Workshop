# Informe de implementación y verificación

**Proyecto:** SDN Controller + Router — Sesión 2  
**Fecha:** 27 de octubre de 2026  
**Estado:** implementación empaquetada; verificaciones ejecutadas en este entorno.

## Decisión de línea base

Se implementó T1 de los seis documentos aprobados de la Sesión 1 como `data/topology.json`: nodos A–D y enlaces A–B, B–D, A–C y C–D. El ejercicio de seis nodos A–F que aparece en el PDF del equipo se registró como `DISC-001` en `docs/discrepancy-log.md`; no reemplaza T1. Los seis documentos de especificación en `specs/` se compararon con los archivos aprobados de entrada y permanecen sin cambios.

## Verificaciones ejecutadas

| Verificación | Resultado observado |
|---|---|
| Suite automatizada | 26 passed (`python -m pytest -q`) |
| Compilación de módulos | `python -m compileall -q controller router tests scripts`: PASS |
| Línea base JSON | 4 nodos, 4 enlaces; coincide con T1 |
| Integración HTTP independiente | PASS: health, ruta inicial, entrega de paquete, fallos/restauración de enlaces, ausencia de ruta y versiones 1–4 |
| NFR-10, delay | p95 nearest-rank 2.842 ms frente a umbral 200 ms: cumple en este entorno |
| NFR-10, bandwidth | p95 nearest-rank 2.529 ms frente a umbral 200 ms: cumple en este entorno |
| NFR-10, loss | p95 nearest-rank 2.438 ms frente a umbral 200 ms: cumple en este entorno |
| NFR-11, caída de Controller | 10/10 solicitudes devolvieron 503 `CONTROLLER_UNAVAILABLE` dentro de 3 s; salud de Router 200 y recuperación posterior 200 |

NFR-10 usa una topología sintética de 50 nodos y 150 enlaces, con 100 solicitudes medidas por métrica, excluyendo tres calentamientos por métrica. NFR-11 detiene Controller, mantiene Router activo y vuelve a iniciar Controller. Las latencias dependen de la máquina y no son una garantía de producción.

## Evidencias

- `test-results.txt`: salida real de la suite pytest.
- `nfr-results.json`: muestras individuales y resumen de las pruebas NFR ejecutadas.
- `demo-evidence/http-integration-results.json`: respuestas observadas en la integración de procesos HTTP independientes.
- `docs/discrepancy-log.md`: decisión y comparación de topologías.

## Cómo reproducir

Desde la raíz del proyecto, con Python 3.11 o superior:

```bash
python -m pip install -r requirements.txt
python -m pytest -q
python scripts/verify_nfr.py
```

Para integración manual, ejecute `python -m controller.run` y `python -m router.run` en dos terminales. La guía de configuración para PyCharm está en `README.md`.

## Alcance y limitaciones

La solución es una simulación educativa a nivel de aplicación. No transmite tráfico real ni implementa OpenFlow. El estado operativo de enlaces vive en memoria y vuelve al estado inicial al reiniciar Controller. La métrica `bandwidth` usa el costo aditivo `1/b` por enlace, tal como documenta el README; no representa maximización del ancho de banda mínimo del camino.
