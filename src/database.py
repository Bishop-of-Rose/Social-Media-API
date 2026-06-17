from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import settings

DATABASE_URL = (f"postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@"
                f"{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")

engine = create_engine(DATABASE_URL)
session = sessionmaker(bind=engine)
Base = declarative_base()

def get_session():
    db = session()
    try:
        yield db
    finally:
        db.close()
