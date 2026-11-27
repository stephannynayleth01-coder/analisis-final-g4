# Reporte de la corrida

- Fecha: 2026-11-27 00:00
- Spec: `specs/spec_final.md`
- Origen del modelo: LLM ollama / qwen2.5:7b
- Intentos al LLM: 2
- Duración de la extracción: 229.9 s

## Revisión de la spec (sin LLM)

- Sin observaciones.

## Validación del modelo generado

Intento 1 fallido:
  - Entidad Personaje no indica req_ids (trazabilidad).
  - Entidad Mision no indica req_ids (trazabilidad).
  - Entidad IntentoMision no indica req_ids (trazabilidad).

## Cobertura declarada por el modelo

- Requerimientos con elementos asociados: 10 de 21
- ⚠️ Sin cobertura: RN-01, RN-02, RN-03, RN-04, RN-05, RN-06, RN-07, RN-08

> Que el modelo *declare* cubrir un requerimiento no significa que lo cubra bien.
> Verifica cada fila de `trazabilidad_generada.csv` contra la spec y los diagramas.
