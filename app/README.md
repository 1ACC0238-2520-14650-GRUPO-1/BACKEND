# API de Gestión de Postulaciones (carpeta `app`)

Instrucciones y dependencias para ejecutar la aplicación FastAPI incluida en esta carpeta.

Requisitos
- Python 3.10+
- PostgreSQL (opcional, la aplicación tiene un modo de fallback)

Instalación (Windows PowerShell)
```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt
```

Crear archivo de variables de entorno:
```powershell
copy .env.example .env
# editar .env con las credenciales de tu BD
```

Ejecutar
```powershell
python ..\run_safe.py
# o directamente:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Notas
- En Windows puede haber problemas al cargar `psycopg2` por DLLs; se recomienda usar `psycopg2-binary`.
- Si no quieres usar la BD, `run_safe.py` detecta y arranca una versión alternativa o limitada.
