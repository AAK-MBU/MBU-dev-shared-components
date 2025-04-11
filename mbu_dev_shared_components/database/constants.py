"""This module handles generating and fetching constants and credentials from the database"""

import os
import pyodbc
from datetime import datetime

from mbu_dev_shared_components.utils.fernet_encryptor import Encryptor
from mbu_dev_shared_components.database.utility import connect_to_db, execute_query


def add_credential(
        credential_name: str,
        username: str,
        password: str,
        changed_at: datetime = datetime.now(),
        db_env: str = "PROD"
):
    encryptor = Encryptor()
    encrypted_password = encryptor.encrypt(password)

    rpa_conn = connect_to_db(db_env=db_env)
    cursor = rpa_conn.cursor()

    query = """
        INSERT INTO [RPA].[rpa].[Credentials]
            ([name]
            ,[username]
            ,[password]
            ,[changed_at])
        VALUES
            (?
            ,?
            ,?
            ,?)
        """
    params = [credential_name, username, encrypted_password, changed_at]
    execute_query(query=query, cursor=cursor, params=params)


def get_credential(
        credential_name: str,
        db_env: str = "PROD"
    ) -> dict:
    
    rpa_conn = connect_to_db(db_env=db_env)
    cursor = rpa_conn.cursor()
    encryptor = Encryptor()

    query = """
        SELECT 
            Username
            ,cast(Password as varbinary(max))
        FROM [RPA].[rpa].[Credentials]
        WHERE
            name = ?
        """
    
    params = [credential_name]

    res = execute_query(query=query, cursor=cursor, params=params)
    if res is not None:
        res = res[0]
        username = res[0]
        encrypted_password = res[1]

        decrypted_password = encryptor.decrypt(encrypted_password)

        return  {
            "username": username, 
            "decrypted_password": decrypted_password, 
            "encrypted_password": encrypted_password
        } 
    else:
        print(f"No credential found with name {credential_name}")

def get_constant(
        constant_name: str,
        db_env: str = "PROD"
    ) -> tuple:
    
    rpa_conn = connect_to_db(db_env=db_env)
    cursor = rpa_conn.cursor()
    encryptor = Encryptor()

    query = """
        SELECT 
            name
            ,value
        FROM [RPA].[rpa].[Constants]
        WHERE
            name = ?
        """
    
    params = [constant_name]

    res = execute_query(query=query, cursor=cursor, params=params)
    if res is not None:

        returned_constant = res[0]
        constant_name = returned_constant[0]
        value = returned_constant[1]

        return {"constant_name": constant_name, "value": value}
    else:
        print(f"No constant found with name: {constant_name}")


def add_constant(
        constant_name: str,
        value: str,
        changed_at: datetime = datetime.now(),
        db_env: str = "PROD"
):
    query = """
        INSERT INTO [RPA].[rpa].[Constants]
            ([name]
            ,[value]
            ,[changed_at])
        VALUES
            (?
            ,?
            ,?)
        """
    
    rpa_conn = connect_to_db(db_env=db_env)
    cursor = rpa_conn.cursor()

    params = [constant_name, value, changed_at]
    execute_query(query=query, cursor=cursor, params=params)


