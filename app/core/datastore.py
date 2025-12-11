"""
This module is used to connect to Datastore
"""
from typing import Dict
from typing import Optional

from decouple import config

from snowflake.sqlalchemy import URL
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import QueuePool


# Connected datastores
# Maintain connected objects for each company
#   Return the existing factory object on subsequent calls
connected_datastores: Dict[str, sessionmaker] = {}


def get_datastore() -> Optional[sessionmaker]:
    """
    This function is used to get the datastore connection

    :return: sqlalchemy.orm.sessionmaker - Database session factory
             Use the session factory to create db sessions
    """
    # Check if the enabled datastore is supported

    # Check if there is a connected datastore for the database
    if config("SNOWFLAKE_DATABASE") in connected_datastores:
        return connected_datastores[config("SNOWFLAKE_DATABASE")]

    # Snowflake engine

    # Fetch credentials from env
    # Create sqlalchemy engine
    engine_url = URL(
        account=config("SNOWFLAKE_ACCOUNT"),
        user=config("SNOWFLAKE_USER"),
        password=config("SNOWFLAKE_PASSWORD"),
        database=config("SNOWFLAKE_DATABASE"),
        schema=config("SNOWFLAKE_SCHEMA"),
        warehouse=config("SNOWFLAKE_WAREHOUSE"),
    )
    engine = create_engine(
        url=engine_url,
        connect_args={
            "client_session_keep_alive": True,
            "client_session_keep_alive_heartbeat_frequency": 900,
        },
        poolclass=QueuePool,
        pool_size=20,
        max_overflow=20,
    )

    # Create session factory
    session_factory = sessionmaker(bind=engine)
    connected_datastores[config("SNOWFLAKE_DATABASE")] = session_factory
    return session_factory
