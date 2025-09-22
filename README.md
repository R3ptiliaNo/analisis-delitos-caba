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
git clone https://github.com/tu_usuario/tu_repo.git
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
CREATE DATABASE dashboard_db;
O desde shell:

bash
Copiar código
psql -U postgres -c "CREATE DATABASE dashboard_db;"
Verificar que PostgreSQL está corriendo y podés conectarte:

bash
Copiar código
# ejemplo: conectarse a psql con el usuario postgres
psql -U postgres -h localhost -p 5432 -d postgres
Si te pide contraseña, ingresala (o configurala según tu instalación).