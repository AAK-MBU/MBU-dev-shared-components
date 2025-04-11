"""This module handles general database connection and calls"""

import os
import pyodbc
from datetime import datetime

def connect_to_db(autocommit=True, db_env="PROD") -> pyodbc.Connection:
    """Establish connection to sql database

    Returns:
        rpa_conn (pyodbc.Connection): The connection object to the SQL database.
    """
    connection_env = fetch_env(db_env)
    rpa_conn_string = os.getenv(connection_env)
    rpa_conn = pyodbc.connect(rpa_conn_string, autocommit=autocommit)
    return rpa_conn

def execute_query(query: str, cursor: pyodbc.Cursor, params: list) -> pyodbc.Cursor:
    is_select = query.strip().upper().startswith('SELECT')
    try:
        res = cursor.execute(query, params)
        if is_select:
            res = cursor.fetchall()
            if len(res) == 0:
                print("No results from query")
                return None
            return res
        else:
            return None
    except pyodbc.Error as e:
        print(e)
    finally:
        cursor.close()


def fetch_env(db_env):
    if db_env.upper() == "PROD":
        connection_env = "DbConnectionString"
        return connection_env
    if db_env.upper() == "TEST":
        connection_env = "DbConnectionStringTest"
        return connection_env
    
    raise ValueError(f"arg db_env is {db_env.upper()} but should be 'PROD' or 'TEST'")