# app.py (modificado para usar conexión a Postgres)

import os
import pandas as pd
import streamlit as st
from datetime import datetime
from sqlalchemy import create_engine, text
# load_data.py (inicio del archivo — cargas las credenciales desde configuracion_contraseñas.py)
import os

def _missing_credentials_msg(missing):
    return (
        "No se encontraron credenciales completas para la DB.\n"
        "Faltan: " + ", ".join(missing) + ".\n\n"
        "Opciones:\n"
        " 1) Crear un archivo local 'configuracion_contraseñas.py' con las variables: "
        "DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME, TABLE_NAME\n"
        " 2) Exportar las mismas variables en el entorno (ej: export DB_USER=... / set DB_USER=...)\n"
        "Ejemplo de 'configuracion_contraseñas.py' (NO subir al repo):\n"
        "DB_USER = 'postgres'\nDB_PASS = 'tu_password'\nDB_HOST = 'localhost'\nDB_PORT = '5432'\nDB_NAME = 'dashboard_db'\nTABLE_NAME = 'delitos'\n"
    )

# Intento de cargar credenciales desde el archivo local 'configuracion_contraseñas.py'
try:
    import configuracion_contraseñas as cfg  # archivo local editable por cada usuario
    DB_USER = getattr(cfg, "DB_USER", None)
    DB_PASS = getattr(cfg, "DB_PASS", None)
    DB_HOST = getattr(cfg, "DB_HOST", None)
    DB_PORT = getattr(cfg, "DB_PORT", None)
    DB_NAME = getattr(cfg, "DB_NAME", None)
    TABLE_NAME = getattr(cfg, "TABLE_NAME", None)

    missing = [k for k, v in (
        ("DB_USER", DB_USER),
        ("DB_PASS", DB_PASS),
        ("DB_HOST", DB_HOST),
        ("DB_PORT", DB_PORT),
        ("DB_NAME", DB_NAME),
        ("TABLE_NAME", TABLE_NAME),
    ) if not v]
    if missing:
        raise RuntimeError(_missing_credentials_msg(missing))

except ImportError:
    # Si no existe el archivo local, usar variables de entorno
    DB_USER = os.getenv("DB_USER")
    DB_PASS = os.getenv("DB_PASS")
    DB_HOST = os.getenv("DB_HOST")
    DB_PORT = os.getenv("DB_PORT")
    DB_NAME = os.getenv("DB_NAME")
    TABLE_NAME = os.getenv("TABLE_NAME")

    missing = [k for k, v in (
        ("DB_USER", DB_USER),
        ("DB_PASS", DB_PASS),
        ("DB_HOST", DB_HOST),
        ("DB_PORT", DB_PORT),
        ("DB_NAME", DB_NAME),
        ("TABLE_NAME", TABLE_NAME),
    ) if not v]
    if missing:
        raise RuntimeError(_missing_credentials_msg(missing))


@st.cache_data(ttl=300)
def load_data():
    """
    Carga los datos desde Postgres con caching para mejor performance
    """
    try:
        engine = create_engine(
            f"postgresql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
        )
        query = text(f"SELECT * FROM {TABLE_NAME}")
        df = pd.read_sql(query, engine)

        # Convertir fecha a datetime
        if 'fecha' in df.columns:
            df['fecha'] = pd.to_datetime(df['fecha'], errors='coerce')

        # Asegurarse de que latitud y longitud sean numéricas
        if 'latitud' in df.columns and 'longitud' in df.columns:
            df['latitud'] = pd.to_numeric(df['latitud'], errors='coerce')
            df['longitud'] = pd.to_numeric(df['longitud'], errors='coerce')
            df = df.dropna(subset=['latitud', 'longitud'])

        # Ordenar por fecha si existe
        if 'fecha' in df.columns:
            df = df.sort_values('fecha')

        return df
    except Exception as e:
        st.error(f"Error al cargar los datos desde Postgres: {e}")
        return None

def filter_data(df, tipo_delito=None, comuna=None, barrio=None, fecha_inicio=None, fecha_fin=None):
    """
    Filtra el dataframe según los parámetros seleccionados
    """
    df_filtered = df.copy()

    if tipo_delito and tipo_delito != "Todos" and 'tipo' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['tipo'] == tipo_delito]

    if comuna and comuna != "Todas" and 'comuna' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['comuna'] == comuna]

    if barrio and barrio != "Todos" and 'barrio' in df_filtered.columns:
        df_filtered = df_filtered[df_filtered['barrio'] == barrio]

    if 'fecha' in df_filtered.columns:
        if fecha_inicio:
            fecha_inicio = pd.to_datetime(fecha_inicio)
            df_filtered = df_filtered[df_filtered['fecha'] >= fecha_inicio]

        if fecha_fin:
            fecha_fin = pd.to_datetime(fecha_fin)
            df_filtered = df_filtered[df_filtered['fecha'] <= fecha_fin]

    return df_filtered
