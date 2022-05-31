from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# SQL_ALCHEMY_DATABASE_URL = 'sqlite:///./apps/database.db'
SQL_ALCHEMY_DATABASE_URL = 'mysql+pymysql://root:@localhost:3306/fastapipostku'
engine = create_engine(SQL_ALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
