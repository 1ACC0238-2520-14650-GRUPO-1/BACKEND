"""
Archivo connection_fallback.py que se puede usar como alternativa 
cuando psycopg2 falla al cargar por problemas de DLL en Windows.
"""
import time
import logging
import importlib.util
import subprocess
import sys
import os
import platform

# Configuración de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intentar importar sqlalchemy pero sin depender directamente de psycopg2
def is_module_available(module_name):
    """Verifica si un módulo está disponible para importar"""
    return importlib.util.find_spec(module_name) is not None

def get_database_config():
    """Obtiene la configuración de la base de datos"""
    from app.config import settings
    
    return {
        'user': settings.DB_USER,
        'password': settings.DB_PASSWORD,
        'host': settings.DB_HOST,
        'port': settings.DB_PORT,
        'database': settings.DB_NAME,
        'database_url': settings.DATABASE_URL
    }

def check_postgres_connection_with_psql():
    """Verifica la conexión a PostgreSQL usando psql.exe en Windows"""
    if platform.system() != "Windows":
        return False

    # Buscar psql en las ubicaciones comunes de Windows
    psql_paths = [
        "C:\\Program Files\\PostgreSQL\\17\\bin\\psql.exe",
        "C:\\Program Files\\PostgreSQL\\16\\bin\\psql.exe",
        "C:\\Program Files\\PostgreSQL\\15\\bin\\psql.exe",
        "C:\\Program Files\\PostgreSQL\\14\\bin\\psql.exe",
        "C:\\Program Files\\PostgreSQL\\13\\bin\\psql.exe",
    ]
    
    psql_path = None
    for path in psql_paths:
        if os.path.exists(path):
            psql_path = path
            break
    
    if not psql_path:
        return False

    try:
        # Obtener configuración de la DB
        db_config = get_database_config()
        
        # Intentar conectarse con psql
        cmd = [
            psql_path, 
            "-h", db_config['host'], 
            "-p", db_config['port'], 
            "-U", db_config['user'], 
            "-c", "SELECT 1", 
            "postgres"
        ]
        
        # Configurar la contraseña como variable de entorno
        env = os.environ.copy()
        env["PGPASSWORD"] = db_config['password']
        
        # Ejecutar psql con un timeout
        result = subprocess.run(
            cmd,
            env=env,
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            logger.info("Conexión exitosa a PostgreSQL usando psql")
            return True
        else:
            logger.error(f"Error al conectar a PostgreSQL: {result.stderr}")
            return False
    except Exception as e:
        logger.error(f"Error al conectar a PostgreSQL usando psql: {e}")
        return False

def setup_database_connection():
    """
    Configura una conexión a la base de datos de manera robusta,
    manejando diferentes escenarios de error.
    """
    # Intentar importar SQLAlchemy
    if not is_module_available('sqlalchemy'):
        logger.error("SQLAlchemy no está disponible. Instálalo con: pip install sqlalchemy")
        return None, None, None

    # Verificar si tenemos psycopg2
    has_psycopg2 = is_module_available('psycopg2')
    has_psycopg2_binary = is_module_available('psycopg2-binary')
    
    if not (has_psycopg2 or has_psycopg2_binary):
        logger.warning("No se encontró psycopg2 ni psycopg2-binary. Intenta instalarlos con: pip install psycopg2-binary")
        
        # Verificar si al menos podemos usar psql para verificar la conexión
        if check_postgres_connection_with_psql():
            logger.info("Se verificó la conexión con psql, pero se necesita psycopg2 para la aplicación.")
            logger.info("Intentando continuar con configuración mínima...")
        else:
            logger.error("No se puede conectar a PostgreSQL. Verifica la instalación y la configuración.")
            return None, None, None
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.ext.declarative import declarative_base
        from sqlalchemy.orm import sessionmaker
        
        # Obtener configuración
        db_config = get_database_config()
        
        # Intentar crear el motor
        try:
            engine = create_engine(
                db_config['database_url'],
                echo=False,
                pool_pre_ping=True,
                pool_recycle=3600,
                connect_args={"connect_timeout": 10}
            )
            logger.info("Motor de SQLAlchemy creado exitosamente.")
        except Exception as e:
            logger.error(f"Error al crear el motor de SQLAlchemy: {e}")
            engine = None
        
        # Crear una clase Base
        Base = declarative_base()
        
        # Crear una fábrica de sesiones
        if engine:
            SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        else:
            SessionLocal = None
            logger.warning("No se pudo crear SessionLocal porque el motor es None")
        
        return engine, SessionLocal, Base
    except Exception as e:
        logger.error(f"Error al configurar la conexión a la base de datos: {e}")
        return None, None, None

def get_db():
    """
    Función para obtener una sesión de base de datos.
    """
    from app.config import settings
    
    # Importaciones locales para evitar errores de importación circulares
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    
    # Recrear el motor y la sesión aquí para asegurar que sean actuales
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Error al obtener sesión de DB: {e}")
        raise

# Configurar la conexión inicial
engine, SessionLocal, Base = setup_database_connection()