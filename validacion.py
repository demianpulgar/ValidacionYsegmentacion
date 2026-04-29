"""
Pipeline de Datos – Validación Estructural y Semántica
Actividad 2.3 - DuocUC
"""

import pandas as pd
import re
import logging
import os
from datetime import datetime

# ─────────────────────────────────────────
#  CONFIGURACIÓN DE LOGS
# ─────────────────────────────────────────
os.makedirs("output", exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("output/validacion.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
log = logging.getLogger(__name__)

# ─────────────────────────────────────────
#  CONSTANTES / REGLAS DE NEGOCIO
# ─────────────────────────────────────────
COLUMNAS_REQUERIDAS = ["id", "nombre", "edad", "ciudad", "fecha_compra", "monto", "metodo_pago"]
FORMATO_FECHA       = r"^\d{4}-\d{2}-\d{2}$"          # YYYY-MM-DD
EDAD_MIN, EDAD_MAX  = 0, 120
METODOS_VALIDOS     = {"tarjeta", "efectivo", "transferencia", "debito"}
MONTO_MIN           = 0


# ══════════════════════════════════════════
#  BLOQUE 1 – VALIDACIONES ESTRUCTURALES
# ══════════════════════════════════════════

def validar_columnas(df: pd.DataFrame) -> list[str]:
    """V-E1: Verifica que existan todas las columnas requeridas."""
    faltantes = [c for c in COLUMNAS_REQUERIDAS if c not in df.columns]
    if faltantes:
        log.error(f"[V-E1] Columnas faltantes: {faltantes}")
    else:
        log.info("[V-E1] ✔ Todas las columnas requeridas están presentes.")
    return faltantes


def validar_tipos_nulos(df: pd.DataFrame) -> pd.Series:
    """
    V-E2: Detecta valores nulos o vacíos en campos obligatorios.
    Retorna una máscara booleana (True = fila con error).
    """
    mask = pd.Series(False, index=df.index)
    for col in ["nombre", "edad", "monto"]:
        col_vacia = df[col].astype(str).str.strip() == ""
        nuevos    = col_vacia & ~mask
        if nuevos.any():
            for idx in df[nuevos].index:
                log.warning(f"[V-E2] Fila {idx+1}: campo '{col}' nulo/vacío → {dict(df.loc[idx])}")
        mask |= col_vacia
    return mask


def validar_formato_fecha(df: pd.DataFrame) -> pd.Series:
    """
    V-E3: Verifica que fecha_compra tenga el formato YYYY-MM-DD.
    Retorna una máscara booleana (True = fila con error).
    """
    mask = ~df["fecha_compra"].astype(str).str.strip().str.match(FORMATO_FECHA)
    for idx in df[mask].index:
        log.warning(f"[V-E3] Fila {idx+1}: fecha inválida '{df.at[idx,'fecha_compra']}' — se esperaba YYYY-MM-DD")
    if not mask.any():
        log.info("[V-E3] ✔ Todas las fechas tienen formato correcto.")
    return mask


def validar_monto_numerico(df: pd.DataFrame) -> pd.Series:
    """
    V-E4: Verifica que 'monto' sea numérico y positivo (>= 0).
    Retorna una máscara booleana (True = fila con error).
    """
    def es_invalido(v):
        try:
            return float(str(v).strip()) < MONTO_MIN
        except (ValueError, TypeError):
            return True

    mask = df["monto"].apply(es_invalido)
    for idx in df[mask].index:
        log.warning(f"[V-E4] Fila {idx+1}: monto inválido '{df.at[idx,'monto']}'")
    if not mask.any():
        log.info("[V-E4] ✔ Todos los montos son numéricos y positivos.")
    return mask


# ══════════════════════════════════════════
#  BLOQUE 2 – VALIDACIONES SEMÁNTICAS
# ══════════════════════════════════════════

def validar_rango_edad(df: pd.DataFrame) -> pd.Series:
    """
    V-S1: La edad debe estar entre EDAD_MIN y EDAD_MAX.
    Retorna una máscara booleana (True = fila con error).
    """
    def fuera_de_rango(v):
        try:
            edad = int(float(str(v).strip()))
            return not (EDAD_MIN <= edad <= EDAD_MAX)
        except (ValueError, TypeError):
            return True

    mask = df["edad"].apply(fuera_de_rango)
    for idx in df[mask].index:
        log.warning(f"[V-S1] Fila {idx+1}: edad fuera de rango [{EDAD_MIN}-{EDAD_MAX}] → '{df.at[idx,'edad']}'")
    if not mask.any():
        log.info("[V-S1] ✔ Todas las edades están dentro del rango aceptable.")
    return mask


def validar_metodo_pago(df: pd.DataFrame) -> pd.Series:
    """
    V-S2: El método de pago debe ser uno de los valores aceptados
    (sin distinguir mayúsculas/minúsculas).
    Retorna una máscara booleana (True = fila con error).
    """
    mask = ~df["metodo_pago"].astype(str).str.strip().str.lower().isin(METODOS_VALIDOS)
    for idx in df[mask].index:
        log.warning(f"[V-S2] Fila {idx+1}: método de pago inválido '{df.at[idx,'metodo_pago']}' "
                    f"— valores válidos: {METODOS_VALIDOS}")
    if not mask.any():
        log.info("[V-S2] ✔ Todos los métodos de pago son válidos.")
    return mask


def validar_duplicados(df: pd.DataFrame) -> pd.Series:
    """
    V-S3 (semántica): No deben existir registros duplicados por 'id'.
    Retorna una máscara booleana (True = fila duplicada).
    """
    mask = df.duplicated(subset=["id"], keep="first")
    for idx in df[mask].index:
        log.warning(f"[V-S3] Fila {idx+1}: id duplicado '{df.at[idx,'id']}'")
    if not mask.any():
        log.info("[V-S3] ✔ No se encontraron IDs duplicados.")
    return mask


# ══════════════════════════════════════════
#  PIPELINE PRINCIPAL
# ══════════════════════════════════════════

def ejecutar_pipeline(ruta_entrada: str):
    log.info("=" * 60)
    log.info("  INICIO DEL PIPELINE DE VALIDACIÓN")
    log.info(f"  Archivo: {ruta_entrada}")
    log.info(f"  Fecha:   {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    log.info("=" * 60)

    # 1. CARGA
    df = pd.read_csv(ruta_entrada, dtype=str)
    log.info(f"Registros cargados: {len(df)}")

    # 2. VALIDACIÓN ESTRUCTURAL – columnas
    faltantes = validar_columnas(df)
    if faltantes:
        log.error("Pipeline detenido: faltan columnas críticas.")
        return

    # 3. INICIALIZAR MÁSCARA DE ERRORES
    mask_error = pd.Series(False, index=df.index)

    # 4. VALIDACIONES ESTRUCTURALES
    mask_error |= validar_tipos_nulos(df)
    mask_error |= validar_formato_fecha(df)
    mask_error |= validar_monto_numerico(df)

    # 5. VALIDACIONES SEMÁNTICAS
    mask_error |= validar_rango_edad(df)
    mask_error |= validar_metodo_pago(df)
    mask_error |= validar_duplicados(df)

    # 6. SEPARACIÓN DE REGISTROS
    df_validos   = df[~mask_error].copy()
    df_invalidos = df[mask_error].copy()

    # 7. EXPORTACIÓN
    df_validos.to_csv("output/ventas_validas.csv",   index=False, encoding="utf-8")
    df_invalidos.to_csv("output/ventas_invalidas.csv", index=False, encoding="utf-8")

    # 8. RESUMEN FINAL
    log.info("-" * 60)
    log.info(f"  RESUMEN FINAL")
    log.info(f"  Total registros    : {len(df)}")
    log.info(f"  ✔ Registros válidos  : {len(df_validos)}")
    log.info(f"  ✘ Registros inválidos: {len(df_invalidos)}")
    log.info(f"  Archivos generados en /output/")
    log.info("=" * 60)

    return df_validos, df_invalidos


if __name__ == "__main__":
    ejecutar_pipeline("ventas_sucias.csv")
