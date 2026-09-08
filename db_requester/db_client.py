from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from resources.credits import credits

USERNAME = credits.MOVIES_DB_USER
PASSWORD = credits.MOVIES_DB_PASSWORD
HOST = credits.MOVIES_DB_HOST
PORT = credits.MOVIES_DB_PORT
DATABASE_NAME = credits.MOVIES_DB_NAME

engine = create_engine(
    f"postgresql+psycopg2://{USERNAME}:{PASSWORD}@{HOST}:{PORT}/{DATABASE_NAME}",
    echo=False  # Установить True для отладки SQL запросов
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db_session():
    """Создает новую сессию БД"""
    return SessionLocal()