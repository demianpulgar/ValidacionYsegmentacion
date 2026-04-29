# Pipeline de Datos – Validación Estructural y Semántica
**Actividad 2.3 · DuocUC · Informática y Telecomunicaciones**

---

## Descripción

Script Python que implementa un pipeline de validación sobre el dataset `ventas_sucias.csv`, el cual contiene errores intencionados. El objetivo es detectar, registrar y separar los registros inválidos de los válidos antes de la etapa de carga a base de datos.

---

## Estructura del proyecto

```
validador/
├── validacion.py          # Script principal modularizado
├── ventas_sucias.csv      # Dataset de entrada (no se modifica)
└── output/
    ├── ventas_validas.csv   # Registros que pasaron todas las validaciones
    ├── ventas_invalidas.csv # Registros con al menos un error detectado
    └── validacion.log       # Log detallado de cada error encontrado
```

---

## Cómo ejecutar

```bash
python validacion.py
```

Requiere Python 3.10+ y `pandas` instalado (`pip install pandas`).

---

## Validaciones implementadas

### Estructurales (V-E)

| Código | Validación | Justificación técnica |
|--------|-----------|----------------------|
| V-E1 | Columnas requeridas presentes | Sin las columnas clave el pipeline no puede continuar |
| V-E2 | Sin valores nulos/vacíos en `nombre`, `edad`, `monto` | Campos obligatorios para identificar al cliente y el monto de la venta |
| V-E3 | Formato de fecha `YYYY-MM-DD` (regex) | Formato ISO 8601 requerido para carga en base de datos |
| V-E4 | `monto` numérico y >= 0 | Un monto negativo o no numérico es técnicamente inválido |

### Semánticas (V-S)

| Código | Validación | Justificación de negocio |
|--------|-----------|--------------------------|
| V-S1 | `edad` entre 0 y 120 | Una edad fuera de ese rango es biológicamente imposible |
| V-S2 | `metodo_pago` ∈ {tarjeta, efectivo, transferencia, debito} | Solo se aceptan medios de pago registrados en el sistema |
| V-S3 | Sin IDs duplicados | Un `id` repetido viola la unicidad del registro de venta |

---

## Errores detectados en el dataset

| Fila | Error |
|------|-------|
| 2 | `edad` vacía, fecha con formato `DD/MM/YYYY` |
| 3 | Fecha con formato `YYYY/MM/DD` |
| 4 | `monto` vacío |
| 6 | `id` duplicado (igual a fila 5) |
| 7 | `edad` = 150, fuera del rango biológico |
| 9 | `nombre` vacío |

---

## Decisiones técnicas

- **No se modifica el archivo de entrada**: el CSV original se lee en modo lectura pura.
- **Funciones separadas por tipo de validación**: permite reutilizar y testear cada regla de forma independiente.
- **Logging dual** (consola + archivo): facilita el monitoreo en tiempo real y la auditoría posterior.
- **Máscara acumulativa de errores**: un registro se marca como inválido si falla *cualquier* validación, evitando duplicar filas en la salida.
- **dtype=str en lectura**: se carga todo como texto para no perder información en la detección de errores de tipo.
