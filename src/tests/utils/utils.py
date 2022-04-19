import psycopg2
from psycopg2 import sql
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

from core.config import config


def drop_test_database():
    db_connection = psycopg2.connect(
        host=config.POSTGRES_HOST,
        database=config.POSTGRES_TEST_DATABASE,
        user=config.POSTGRES_USER_NAME,
        password=config.POSTGRES_USER_PASSWORD,
        port=config.POSTGRES_PORT,
    )
    db_connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)

    db_cursor = db_connection.cursor()
    db_cursor.execute(sql.SQL(
        'DROP DATABASE {}'
    ).format(sql.Identifier(config.POSTGRES_TEST_DATABASE)))