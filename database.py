import os
from dotenv import load_dotenv
from sqlmodel import Session, create_engine

# Carga las variables de entorno desde el archivo .env
load_dotenv()

# Obtiene la URL de la base de datos para SQLite (archivo local 'genesis.db')
DATABASE_URL = "sqlite:///genesis.db"

# Crea el motor de la base de datos 
# (connect_args es necesario en SQLite si usas la base de datos en múltiples hilos/threads como en FastAPI)
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})


# Función que genera la sesión de base de datos para cada petición HTTP
def get_session():
  with Session(engine) as session:
    yield session