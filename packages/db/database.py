from sqlalchemy import create_engine 
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from packages.config.settings import settings

engine = create_engine(
    settings.database_url, #type:ignore
    pool_size=10,
    max_overflow=20
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class Base(DeclarativeBase):
    pass