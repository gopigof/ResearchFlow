import logging
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import scoped_session, sessionmaker, Session

from backend.config import (
    settings,
)  # Assuming your Snowflake credentials are in settings

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    __mapper_args__ = {"eager_defaults": True}


class DatabaseSession:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            logger.info("Created new database session object")
            cls._instance = super().__new__(cls)

            # Snowflake connection string format:
            # snowflake://<user>:<password>@<account>/<database>/<schema>?warehouse=<warehouse>&role=<role>
            snowflake_uri = (
                f"snowflake://{settings.SNOWFLAKE_DB_USER}:{settings.SNOWFLAKE_DB_PASSWORD}@"
                f"{settings.SNOWFLAKE_DB_ACCOUNT}/{settings.SNOWFLAKE_DB_DATABASE}/{settings.SNOWFLAKE_DB_SCHEMA}?warehouse={settings.SNOWFLAKE_DB_WAREHOUSE}&role={settings.SNOWFLAKE_DB_ROLE}"
            )

            cls._instance.db_engine = create_engine(snowflake_uri)
            cls._instance.session_maker = scoped_session(
                sessionmaker(
                    autocommit=False, autoflush=True, bind=cls._instance.db_engine
                )
            )
        return cls._instance

    @classmethod
    def db_session(cls):
        return cls().session_maker()


@contextmanager
def db_session() -> Session:
    _session = DatabaseSession.db_session()
    try:
        yield _session
    except Exception as e:
        raise ValueError(f"Failed to connect to database: {e}")
    finally:
        _session.close()
