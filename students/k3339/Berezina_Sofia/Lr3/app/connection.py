import os
from dotenv import load_dotenv
from sqlmodel import SQLModel, Session, create_engine

load_dotenv()
db_url = os.getenv(
    "DATABASE_URL",
    "postgresql://postgres:postgres@db:5432/time_manager_db",
)

engine = create_engine(db_url, echo=os.getenv("SQL_ECHO", "false").lower() == "true")

def init_db():
    """Инициализация базы данных"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Получение сессии базы данных"""
    with Session(engine) as session:
        yield session
