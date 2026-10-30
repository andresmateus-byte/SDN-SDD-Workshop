# Registro de discrepancias y decisiones de línea base

Fecha de registro: 27 de octubre de 2026  
Proyecto: SDN Controller + Router — Sesión 2  
Estado: decisión resuelta para la implementación; discrepancia documental conservada.

## DISC-001 — Topología T1 aprobada frente al ejercicio de seis nodos del PDF del equipo

**Tipo:** discrepancia entre fuentes de trabajo.  
**Estado:** resuelta por decisión explícita del usuario.  
**Impacto:** configuración inicial y trazabilidad de pruebas.

### Fuentes implicadas

- Los seis documentos aprobados de la Sesión 1 (`specs/01` a `specs/06`) fijan la topología T1 usada por los casos de aceptación: nodos A, B, C y D, cuatro enlaces y las métricas que aparecen abajo.
- El PDF del equipo `Andres Felipe Mateus Montenegro - Santiago Ramirez Chavarro - w2.docx.pdf` presenta un ejercicio distinto de seis nodos (A–F) con nueve enlaces. No se ha usado ese ejercicio para reemplazar la línea base T1.

### Decisión

Usar exclusivamente T1 como `data/topology.json`. Mantener los seis documentos aprobados sin cambios. Registrar la topología A–F del PDF del equipo como material de un ejercicio separado, no como cambio de requisitos. No ajustar pruebas aprobadas para que coincidan con esa topología alternativa.

### T1 implementada

Nodos: `A`, `B`, `C`, `D`. Todos los enlaces se cargan activos al iniciar Controller; la versión inicial es 1.

| Enlace | Retardo | Ancho de banda | Probabilidad de pérdida |
|---|---:|---:|---:|
| A–B | 10 ms | 100 Mbps | 0.01 |
| B–D | 10 ms | 100 Mbps | 0.01 |
| A–C | 15 ms | 50 Mbps | 0.02 |
| C–D | 20 ms | 50 Mbps | 0.02 |

### Topología alternativa del PDF (solo referencia de discrepancia)

El ejercicio del PDF presenta los siguientes enlaces y métricas; estos valores **no** se copian a `data/topology.json`:

| Enlace | Costo OSPF | Propagación | Capacidad | Pérdida |
|---|---:|---:|---:|---:|
| A–B | 2 | 3 ms | 100 Mbps | 0.2% |
| A–C | 5 | 2 ms | 20 Mbps | 0.8% |
| B–C | 1 | 4 ms | 50 Mbps | 0.4% |
| B–D | 2 | 6 ms | 15 Mbps | 1.0% |
| C–D | 2 | 3 ms | 40 Mbps | 0.3% |
| C–E | 4 | 5 ms | 25 Mbps | 0.5% |
| D–E | 1 | 2 ms | 10 Mbps | 1.5% |
| D–F | 5 | 7 ms | 30 Mbps | 0.2% |
| E–F | 2 | 4 ms | 12 Mbps | 0.6% |

### Verificación de aceptación de T1

- Estado inicial, A→D por `delay`: `A-B-D`, costo 20, versión 1.
- Falla de B–D: A→D por `A-C-D`, costo 35, versión 2.
- Falla adicional de C–D: no existe ruta A→D, versión 3.
- Restauración de B–D: A→D por `A-B-D`, costo 20, versión 4.

Estos comportamientos se comprobaron con procesos HTTP independientes y se guardaron en `demo-evidence/http-integration-results.json`.

### Control de cambios futuro

Si el equipo necesita entregar la topología A–F como requisito, debe aprobarse una nueva versión de requisitos, arquitectura, escenarios dinámicos, contrato/pruebas que dependan de la topología y casos de aceptación. Ese cambio queda fuera de esta implementación y no se aplica implícitamente.

## Nota de nombres del equipo

El nombre del archivo PDF incluye “Andres Felipe Mateus Montenegro” y “Santiago Ramirez Chavarro”, mientras que la especificación de pruebas abrevia/varía el segundo apellido como “Santiago Cavarro”. Se conserva la especificación aprobada intacta; este proyecto usa el nombre del archivo del equipo solo como referencia de procedencia, no como modificación de autoría aprobada.
