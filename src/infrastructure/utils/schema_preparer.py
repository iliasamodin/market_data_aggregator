from collections.abc import Collection

from sqlalchemy import create_engine, text


def create_schemas(
    dsn: str,
    schemas: Collection[str],
) -> None:
    """
    Create schemas in datadase if they don't exist.

    :param dsn: Data source name.
    :param schemas: Schemas to create.
    """

    engine = create_engine(
        dsn,
        isolation_level="AUTOCOMMIT",
    )
    with engine.connect() as connection:
        for schema in schemas:
            stmt = text(f'CREATE SCHEMA IF NOT EXISTS "{schema}";')

            connection.execute(stmt)
