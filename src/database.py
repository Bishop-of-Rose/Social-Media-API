from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

DATABASE_URL = (f"postgresql://{settings.DATABASE_USERNAME}:{settings.DATABASE_PASSWORD}@"
                f"{settings.DATABASE_HOSTNAME}:{settings.DATABASE_PORT}/{settings.DATABASE_NAME}")

engine = create_engine(DATABASE_URL, echo=True)

session = sessionmaker(bind=engine)

class Base(DeclarativeBase):
    pass

def get_session():
    db = session()
    yield db
