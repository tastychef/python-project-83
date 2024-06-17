"""Module for working with database."""

import os
from contextlib import contextmanager
from datetime import datetime

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')


@contextmanager
def launch_connection():
    """Connect with database generator.

    Yields:
        connection with database
    """
    connection = None
    try:
        connection = psycopg2.connect(DATABASE_URL)
        yield connection
    finally:
        if connection:
            connection.close()


class UrlDatabase(object):
    """Storage url data."""

    def save(self, url_data: dict) -> int:
        """Save url data.

        Parameters:
            url_data: page url.

        Returns:
            id of stored url.
        """
        with launch_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO urls(name, created_at)
                    VALUES(%s, %s) RETURNING id;
                    """,
                    (
                        url_data.get('name'),
                        str(datetime.now()),
                    ),
                )
                record = cursor.fetchone()
                connection.commit()
            return record[0]

    def delete(self, url_id: int) -> None:
        """Delete url data from table.

        Parameters:
            url_id: page url.
        """
        with launch_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute('DELETE FROM urls WHERE id=%s;', (url_id,))
                connection.commit()

    def find_all(self, limit: int = 10) -> dict:
        """Find all urls data.

        Parameters:
            limit: urls row on a page.

        Returns:
            selected urls data.
        """
        with launch_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    """
                    SELECT urls.name, ch.status_code, ch.url_id, ch.created_at
                    FROM urls
                    JOIN url_checks as ch
                    ON ch.url_id = urls.id
                    AND ch.created_at IN (
                    SELECT MAX(created_at) FROM url_checks GROUP BY url_id)
                    ORDER BY url_id DESC
                    LIMIT %s;
                    """,
                    (limit, ),
                )
                return cursor.fetchall()

    def find_url_id(self, url_id: int) -> dict:
        """Return url data.

        Parameters:
            url_id: page url.

        Returns:
            stored url data.
        """
        with launch_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    'SELECT * FROM urls WHERE id = %s;',
                    (url_id,),
                )
                return cursor.fetchone()

    def find_url_name(self, url_name: str) -> dict:
        """Return url data.

        Parameters:
            url_name: page url.

        Returns:
            stored url data.
        """
        with launch_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(
                    'SELECT * FROM urls WHERE name = %s;',
                    (url_name,),
                )
                return cursor.fetchone()


class UrlCheckDatabase(object):
    """Storage url checks data."""

    def save_check(self, url_id: int, check_data: dict) -> None:
        """Save url checking data.

        Parameters:
            url_id: url id.
            check_data: data after checking:

                        status_code, h1, title,
                        description.
        """
        with launch_connection() as connection:
            with connection.cursor() as cursor:
                cursor.execute(
                    """
                    INSERT INTO
                    url_checks(
                        url_id,
                        status_code,
                        h1,
                        title,
                        description,
                        created_at)
                    VALUES(%s, %s, %s, %s, %s, %s);""",
                    (
                        url_id,
                        check_data.get('status_code', ''),
                        check_data.get('h1', ''),
                        check_data.get('title', ''),
                        check_data.get('meta', ''),
                        str(datetime.now()),
                    ),
                )
                connection.commit()

    def find_all_checks(self, url_id: int) -> dict:
        """Find all url checking data.

        Parameters:
            url_id: page url.

        Returns:
            data of stored url checking.
        """
        with launch_connection() as connection:
            with connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute(  # noqa: WPS462
                    """
                    SELECT * FROM url_checks
                    WHERE url_id=%s ORDER BY created_at DESC;
                    """,
                    (url_id,),
                )
                return cursor.fetchall()
