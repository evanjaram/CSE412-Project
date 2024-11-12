import psycopg
from . import get_db_connection
from typing import List, Tuple, Optional

"""
    Executes a database query and optionally returns the results.
    
    :param query: The SQL query to execute (as a string).
    :param params: The parameters for parameterized queries (default is None).
    :param fetch_results: Whether to fetch results for SELECT queries (default is False)
                          or to commit results for non-SELECT queries.
    :return: A list of rows for SELECT queries, or None for non-SELECT queries.
"""
def execute_query(query: str, params: Optional[Tuple] = None, fetch_results: bool = False) -> Optional[List[Tuple]]:
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(query, params)

        if fetch_results:
            return cursor.fetchall()
        else:
            connection.commit()
            return None
    except Exception as e:
        print(f"Error executing query: {e}")
        return None
    finally:
        cursor.close()
        connection.close()
