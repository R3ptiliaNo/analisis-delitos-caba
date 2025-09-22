# Dashboard Delitos CABA 2024

Este repositorio contiene una aplicación Streamlit que visualiza y permite analizar los registros de delitos/denuncias de la Ciudad de Buenos Aires para 2024.  
La aplicación obtiene los datos desde una base de datos **PostgreSQL** local (la tabla final que usamos de trabajo se denomina `denuncias`).

> **Fuentes de datos originales**:  
> - Delitos: https://data.buenosaires.gob.ar/dataset/delitos  
> - Comunas (geometría): https://data.buenosaires.gob.ar/dataset/comunas

---

## Requisitos previos

- Python 3.10 o 3.11 (recomendado) instalado.
- PostgreSQL instalado y en ejecución en la máquina local (localhost).
- `psql` disponible en PATH (opcional, útil para verificación).
- Git para clonar el repositorio.

---

## Pasos para clonar y poner en marcha (rápido)

1. Clonar el repositorio:
```bash
git clone https://github.com/R3ptiliaNo/analisis-delitos-caba.git
cd tu_repo
Crear y activar un entorno virtual (recomendado):

bash
Copiar código
# Windows (PowerShell)
python -m venv .venv
.venv\Scripts\Activate.ps1

# Linux / macOS
python -m venv .venv
source .venv/bin/activate
Instalar dependencias:

bash
Copiar código
pip install --upgrade pip
pip install -r requirements.txt
Preparar PostgreSQL
Usaremos una base de datos local. Las credenciales y el nombre de la tabla las configura cada usuario en configuracion_contraseñas.py.

Crear la base de datos (opcional: si no existe). Desde consola psql con un usuario con permisos (ej: postgres):

sql
Copiar código
-- en psql:
CREATE DATABASE denuncias;
O desde shell:

bash
Copiar código
psql -U postgres -c "CREATE DATABASE denuncias;"
Verificar que PostgreSQL está corriendo y podés conectarte:

bash
Copiar código
# ejemplo: conectarse a psql con el usuario postgres
psql -U postgres -h localhost -p 5432 -d postgres
Si te pide contraseña, ingresala (o configurala según tu instalación).

Configurar credenciales locales (obligatorio)

Cada usuario debe crear el archivo local configuracion_contraseñas.py en la raíz del proyecto y llenarlo con sus credenciales. NO subas ese archivo al repo. Hay un configuracion_contraseñas.example.py que sirve como plantilla.

Ejemplo (NO subir) configuracion_contraseñas.py:

# configuracion_contraseñas.py  (archivo LOCAL - no subir)
DB_USER = "postgres"
DB_PASS = "mi_password_local"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "dashboard_db"
TABLE_NAME = "denuncias"   # la tabla final que quedará con los datos del CSV


Alternativa: si preferís usar variables de entorno, exportá las mismas claves DB_USER, DB_PASS, DB_HOST, DB_PORT, DB_NAME, TABLE_NAME antes de ejecutar los scripts.

Asegurate de añadir a .gitignore:

configuracion_contraseñas.py

Cargar los datos (CSV → PostgreSQL)

El script load_data.py toma el CSV local (por defecto data/delitos_2024_clean.csv) y lo carga en la base de datos en la tabla indicada por TABLE_NAME (recomendado: denuncias). El script usa pandas.to_sql y reemplaza la tabla si ya existe.

Ejecutar:

# desde la raíz del repo
python load_data.py --csv data/delitos_2024_clean.csv --table denuncias


O, si preferís que tome la tabla desde configuracion_contraseñas.py, simplemente:

python load_data.py


Qué hace el script

Lee el CSV.

Normaliza nombres de columnas (opcional).

Convierte tipos básicos (fechas, lat/lon).

Crea/reemplaza la tabla denuncias en la DB con los datos del CSV.

Verificar que la tabla fue creada
En psql:

-- listar tablas
\dt
-- contar registros
SELECT COUNT(*) FROM denuncias;
-- ver primeras filas
SELECT * FROM denuncias LIMIT 5;

Ejecutar la aplicación Streamlit

Una vez cargados los datos en la base de datos, lanzá la app:

streamlit run app.py


La aplicación leerá la tabla denuncias desde PostgreSQL usando las credenciales de configuracion_contraseñas.py (o las variables de entorno) y mostrará la interfaz (KPIs, series temporales, mapas, filtros y opciones de exportación).

Recomendaciones y notas útiles

Nombre de la tabla: por convención aquí usamos denuncias. Si preferís otro nombre, cambialo en configuracion_contraseñas.py o pasá --table al load_data.py.

Si el CSV tiene encoding/formatos raros: el script intenta manejar utf-8. Si ves errores de encoding, re-abrí el CSV en un editor y guardalo en UTF-8, o pasá el argumento --encoding latin1 si tu script lo soporta.

Problemas de conexión / UnicodeDecodeError: si te aparece un UnicodeDecodeError al conectar con psycopg2/SQLAlchemy (especialmente en Windows), revisá:

que la contraseña no tenga bytes/bytes no UTF-8,

que no haya variables de entorno relacionadas (PGPASSFILE) apuntando a archivos con encoding raro,

como alternativa, podes ejecutar load_data_fixed.py (incluye fallback para crear la conexión con psycopg2.connect sin construir DSN).

Dependencias geoespaciales: si vas a usar geopandas o funciones espaciales avanzadas, instalalas preferentemente con conda (canal conda-forge) para evitar problemas con GDAL/Fiona en Windows.

Flujo resumido

Clonar repo → git clone ...

Crear env y pip install -r requirements.txt

Instalar/ejecutar PostgreSQL y crear DB dashboard_db

Crear configuracion_contraseñas.py con tus credenciales y poner TABLE_NAME = "denuncias"

Ejecutar python load_data.py (o python load_data.py --csv data/delitos_2024_clean.csv --table denuncias)

Verificar en psql que la tabla denuncias existe y tiene filas

streamlit run app.py → abrir navegador y usar el dashboard

Contacto / contribuciones

Para mejoras, agregar indicadores o capas geo, abrí un issue o hacé un pull request.
Si necesitás ayuda con problemas de instalación en Windows (geopandas/GDAL/psycopg2), indicá tu SO y versión de Python para guiarte.
