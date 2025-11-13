import time
import logging
from sqlalchemy import create_engine, text, exc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from app.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_POSTGRES_URL = f"postgresql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/postgres"

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL

def is_database_available():
    try:
        temp_engine = create_engine(
            DEFAULT_POSTGRES_URL,
            connect_args={"connect_timeout": 5},
            poolclass=None
        )
        
        with temp_engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            return True
    except exc.OperationalError as e:
        logger.error(f"No se pudo conectar a PostgreSQL: {e}")
        return False
    except Exception as e:
        logger.error(f"Error desconocido al verificar PostgreSQL: {e}")
        return False
    finally:
        if 'temp_engine' in locals():
            temp_engine.dispose()

def database_exists(db_name):
    try:
        temp_engine = create_engine(DEFAULT_POSTGRES_URL)
        
        with temp_engine.connect() as connection:
            result = connection.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{db_name}'"))
            exists = result.fetchone() is not None
            return exists
    except Exception as e:
        logger.error(f"Error al verificar si la base de datos existe: {e}")
        return False
    finally:
        if 'temp_engine' in locals():
            temp_engine.dispose()

def create_database():
    if not is_database_available():
        logger.error("PostgreSQL no está disponible. Asegúrate de que el servidor esté en ejecución.")
        return False

    if database_exists(settings.DB_NAME):
        logger.info(f"La base de datos '{settings.DB_NAME}' ya existe.")
        return True

    try:
        temp_engine = create_engine(DEFAULT_POSTGRES_URL)
        
        with temp_engine.connect().execution_options(autocommit=True) as connection:
            connection.execute(text(f"CREATE DATABASE {settings.DB_NAME}"))
            
        logger.info(f"Base de datos '{settings.DB_NAME}' creada exitosamente.")
        return True
    except Exception as e:
        logger.error(f"Error al crear la base de datos: {e}")
        return False
    finally:
        if 'temp_engine' in locals():
            temp_engine.dispose()

try:
    logger.info("Verificando conexión a PostgreSQL...")
    if is_database_available():
        logger.info("Conexión a PostgreSQL establecida.")
        create_database()
    else:
        logger.warning("No se pudo conectar a PostgreSQL. Continuando sin verificar/crear la base de datos.")
except Exception as e:
    logger.error(f"Error durante la inicialización de la base de datos: {e}")

try:
    engine = create_engine(
        SQLALCHEMY_DATABASE_URL, 
        echo=settings.DEBUG,
        pool_pre_ping=True,
        pool_recycle=3600,
        connect_args={
            "connect_timeout": 10,
        }
    )
    logger.info("Motor de SQLAlchemy creado exitosamente.")
except Exception as e:
    logger.error(f"Error al crear el motor de SQLAlchemy: {e}")
    engine = None

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    if engine is None:
        raise Exception("No hay conexión a la base de datos.")
        
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()