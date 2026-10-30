# SDN-SDD-Workshop
Software-Defined Networking (SDN) Controller and Router — Software Design and Development Workshop. Sessions 1 and 2.

# SDN — Taller de Diseño y Desarrollo de Software

## Descripción general del proyecto

Este repositorio contiene los entregables desarrollados para el Taller de Diseño y Desarrollo de Software, centrado en el diseño, la implementación, la integración y la verificación de una simulación de Redes Definidas por Software (SDN, por sus siglas en inglés).

El proyecto consta de dos aplicaciones independientes en Python:

- **Controlador SDN (SDN Controller):** gestiona la topología de la red, los estados de los enlaces y el cálculo de rutas.
- **Enrutador SDN (SDN Router):** se comunica con el Controlador a través de APIs REST y simula el reenvío de paquetes.

## Integrantes del equipo

| Integrante | Responsabilidad |
|---|---|
| Andrés Felipe Mateus | Controlador SDN |
| Santiago Ramirez Chavarro | Enrutador SDN |
| Ambos integrantes | Integración, pruebas y validación |

## Estructura del repositorio

```text
docs/
  session-1/       # Especificaciones de software aprobadas
  session-2/       # Documentación de la implementación

implementation/
  session-2/       # Aplicaciones en Python y pruebas

evidence/
  session-1/       # Evidencias de la sesión 1
  session-2/       # Evidencias de la sesión 2
```

## Entregables del taller

### Sesión 1 — Diseño y especificación de software

Contiene seis documentos en formato Markdown aprobados que abarcan los requisitos, la arquitectura, el comportamiento dinámico, los contratos de API, la planificación de la implementación y las especificaciones de las pruebas.

### Sesión 2 — Implementación, integración y verificación

Contiene el código fuente en Python, la configuración de la topología, las dependencias, las pruebas automatizadas, las instrucciones de ejecución y las evidencias de verificación tanto para el Controlador SDN como para el Enrutador SDN.

## Stack tecnológico

- Python
- FastAPI
- NetworkX
- Pydantic
- HTTPX
- Pytest
- JSON / JSON Lines
- Git y GitHub
- PyCharm

## Cómo ejecutar el proyecto

Consulte el archivo `implementation/session-2/README.md` para obtener instrucciones sobre la instalación, configuración, ejecución y pruebas.

## Estado del proyecto

Simulación educativa de SDN desarrollada como parte del Taller de Diseño y Desarrollo de Software.

El repositorio conserva la línea base aprobada en la Sesión 1 y su trazabilidad con la implementación realizada en la Sesión 2.
