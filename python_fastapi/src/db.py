from sqlalchemy import create_engine, event, QueuePool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


Base = declarative_base()

engine = create_engine(
    "sqlite:///db.sqlite",
    connect_args={"check_same_thread": False},
    poolclass=QueuePool,
    pool_size=2,
)


@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.close()


Base.metadata.bind = engine
session_maker = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = session_maker()
    try:
        yield db
    finally:
        db.close()
