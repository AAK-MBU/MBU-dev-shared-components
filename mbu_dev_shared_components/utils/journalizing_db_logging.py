"""
This module contains functions for updating response data and process status in a database
via stored procedures. The functions utilize the pyodbc library to connect to a database
and execute stored procedures with provided parameters.
"""
import pyodbc


def hub_update_response_data(connection_string: str, step_name: str, json_fragment: str, uuid: str, table_name: str, stored_procedure: str):
    """
    Calls a stored procedure to update response data in the specified table.

    Args:
        connection_string (str): The connection string to connect to the database.
        step_name (str): The name of the step to be updated.
        json_fragment (str): A JSON fragment containing the data to be updated.
        uuid (str): The unique identifier associated with the update.
        table_name (str): The name of the table to be updated.
        stored_procedure (str): The name of the stored procedure to execute.

    Raises:
        Exception: If an error occurs during database connection or execution of the stored procedure.

    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"EXEC {stored_procedure} @StepName = ?, @JsonFragment = ?, @Uuid = ?, @TableName = ?", step_name, json_fragment, uuid, table_name)
                conn.commit()
                print(f"Stored procedure called successfully with step_name: {step_name} for {uuid}")
    except Exception as e:
        print(f"An error occurred: {e}")


def hub_update_process_status(connection_string: str, status: str, uuid: str, table_name: str, stored_procedure: str):
    """
    Calls a stored procedure to update the process status in the specified table.

    Args:
        connection_string (str): The connection string to connect to the database.
        status (str): The new status to be updated.
        uuid (str): The unique identifier associated with the update.
        table_name (str): The name of the table to be updated.
        stored_procedure (str): The name of the stored procedure to execute.

    Raises:
        Exception: If an error occurs during database connection or execution of the stored procedure.

    """
    try:
        with pyodbc.connect(connection_string) as conn:
            with conn.cursor() as cursor:
                cursor.execute(f"EXEC {stored_procedure} @Status = ?, @Uuid = ?, @TableName = ?", status, uuid, table_name)
                conn.commit()
                print(f"Stored procedure called successfully with status: {status} for {uuid}")
    except Exception as e:
        print(f"An error occurred: {e}")
