from sqlalchemy import create_engine 
from sqlalchemy.orm import DeclarativeBase
from packages.config.settings import settings
engine = create_engine(
    settings.database_url, #type:ignore
)
class Base(DeclarativeBase):
    pass