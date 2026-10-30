# Evidencia de demostración en vivo

Guardar aquí capturas de pantalla o video obtenidos por el equipo durante la demostración real. No se incluyen capturas simuladas.

- [ ] Ambos endpoints `/health` responden 200.
- [ ] Paquete A→D entregado por `A-B-D` (costo delay 20).
- [ ] Falla de `B-D`; nuevo paquete usa `A-C-D` (costo delay 35).
- [ ] Restauración de `B-D`; la ruta inicial vuelve a estar disponible.
- [ ] Salida de un test de servicio con `FakeTopologyDAO` o `FakeControllerClient`, sin servidor HTTP.
- [ ] Mostrar `test-results.txt` y `nfr-results.json` de la ejecución local.

- `http-integration-results.json` contiene la salida estructurada de una ejecución real con Controller y Router en procesos HTTP independientes; no es una captura de pantalla.
