from leaflock.database import create_database
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


def get_sessionmaker(database_url: str) -> sessionmaker[Session]:
    create_database(database_url=database_url)
    engine = create_engine(url=database_url)
    return sessionmaker(bind=engine)
