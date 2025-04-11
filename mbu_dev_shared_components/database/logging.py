"""This module handles logging in the RPA database"""

from datetime import datetime
import time
import os
import socket

from mbu_dev_shared_components.database.utility import execute_query, connect_to_db, fetch_env
from mbu_dev_shared_components.utils.db_stored_procedure_executor import execute_stored_procedure

def log_event(
        log_db: str,
        level: str, 
        message: str, 
        context: str, 
        db_env="TEST"
    ):
    created_at = datetime.now()
    """Logs the inputted parameters in """
    query = f"""
        INSERT INTO RPA.{log_db}
            ([level]
            ,[message]
            ,[created_at]
            ,[context])
        VALUES
            (?
            ,?
            ,?
            ,?)
        """
    rpa_conn = connect_to_db(db_env=db_env)
    cursor = rpa_conn.cursor()

    params = [level, message, created_at, context]
    execute_query(query=query, cursor=cursor, params=params)

def _send_heartbeat(
        servicename,
        status,
        details,
        db_env,
):
    conn_env = fetch_env(db_env=db_env)
    conn_str = os.getenv(conn_env)
    hostname = socket.gethostname()
    params = {
        "ServiceName": (str, servicename), 
        "Status": (str, status), 
        "HostName": (str, hostname), 
        "Details": (str, details)
    }
    result = execute_stored_procedure(
        connection_string=conn_str,
        stored_procedure='rpa.sp_UpdateHeartbeat',
        params=params)
    if result["success"] is not True:
        print(result["error_message"])
    
def log_heartbeat(
        stop: str|bool,
        servicename: str,
        heartbeat_interval: int,
        details: str = "",
        db_env: str = "PROD"
    ):
    if isinstance(stop,str):
        stop = stop == "True"
    if not isinstance(heartbeat_interval, int):
        heartbeat_interval = int(heartbeat_interval)
    while not stop:
        status = "RUNNING"
        _send_heartbeat(
            servicename,
            status,
            details,
            db_env,
        )
        time.sleep(heartbeat_interval)
    status = "STOPPED"
    _send_heartbeat(
        servicename,
        status,
        details,
        db_env,
    )