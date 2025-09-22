# load_data_fixed.py
"""

"""
import argparse
import os
import sys
import pandas as pd
from sqlalchemy import create_engine
import psycopg2
import getpass
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


DEFAULT_CSV = 'data/delitos_2024_clean.csv'
DEFAULT_TABLE = 'delitos'

def safe_url_print(user, host, port, db, hide_pass=True):
    pwd = '***' if hide_pass else DB_PASS
    return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

def create_engine_with_fallback(user, password, host, port, db):
    url = f'postgresql://{user}:{password}@{host}:{port}/{db}'
    print("Intentando crear engine con SQLAlchemy (DSN):", safe_url_print(user, host, port, db))
    try:
        engine = create_engine(url)
        # probar una conexión rápida
        conn = engine.connect()
        conn.close()
        print("Conexión exitosa usando la DSN.")
        return engine
    except UnicodeDecodeError as ude:
        print("UnicodeDecodeError detectado al crear la conexión mediante DSN.")
        print("Detalle:", repr(ude))
        print("Intentando fallback usando psycopg2.connect con parámetros separados...")
        # Intentamos crear conexión directa con psycopg2 (pasando params separados)
        try:
            conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db)
            conn.close()
            # Creamos un engine usando un creator que devuelve la conexión psycopg2
            def creator():
                return psycopg2.connect(host=host, port=port, user=user, password=password, dbname=db)
            engine = create_engine('postgresql+psycopg2://', creator=creator)
            # probarla
            c = engine.connect()
            c.close()
            print("Fallback exitoso: engine creado mediante creator + psycopg2.")
            return engine
        except Exception as e2:
            print("Error en fallback con psycopg2.connect. Detalle:")
            raise e2 from ude
    except Exception as e:
        print("Error genérico al crear engine con SQLAlchemy:")
        raise

def load_csv_to_db(csv_path, table_name, engine):
    print(f"Cargando {csv_path} -> tabla {table_name} ...")
    df = pd.read_csv(csv_path, low_memory=False)
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print('Carga finalizada. Registros cargados:', len(df))

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cargar CSV a Postgres (robusto)')
    parser.add_argument('--csv', default=DEFAULT_CSV, help='Ruta al archivo CSV')
    parser.add_argument('--table', default=DEFAULT_TABLE, help='Nombre de la tabla destino')
    parser.add_argument('--db_user', default=DB_USER)
    parser.add_argument('--db_pass', default=DB_PASS)
    parser.add_argument('--db_host', default=DB_HOST)
    parser.add_argument('--db_port', default=DB_PORT)
    parser.add_argument('--db_name', default=DB_NAME)
    args = parser.parse_args()

    # Si usás '-' como password, te pide la contraseña de forma interactiva (más seguro)
    password = args.db_pass
    if password == '-':
        password = getpass.getpass("DB password: ")

    try:
        engine = create_engine_with_fallback(
            user=args.db_user,
            password=password,
            host=args.db_host,
            port=args.db_port,
            db=args.db_name
        )
    except Exception as conn_err:
        print("No se pudo establecer conexión con la base de datos. Mensaje de error completo:")
        import traceback; traceback.print_exc()
        sys.exit(1)

    try:
        load_csv_to_db(args.csv, args.table, engine)
    except Exception:
        print("Error al cargar CSV a la DB. Mensaje completo:")
        import traceback; traceback.print_exc()
        sys.exit(1)
