"""
Module to test RPAConnection functionalities in the Solteq Tand system

Tested functionalities:

    - Establish database connection:
        Function:
            RPAConnection.__enter__
        Assertion:
            Connection and cursor are not None
        Dependencies:
            None

    - Add and retrieve constant:
        Function:
            RPAConnection.add_constant, RPAConnection.get_constant
        Assertion:
            Constant is correctly inserted and retrieved
        Dependencies:
            test_connection

    - Add and retrieve credential:
        Function:
            RPAConnection.add_credential, RPAConnection.get_credential
        Assertion:
            Credential is correctly inserted and retrieved
        Dependencies:
            test_connection

    - Rollback functionality:
        Function:
            RPAConnection.__exit__
        Assertion:
            Constant added without commit is not persisted
        Dependencies:
            test_connection, test_add_get_constant

    - Log event:
        Function:
            RPAConnection.log_event, RPAConnection.get_latest_log
        Assertion:
            Log entry is correctly inserted and retrieved
        Dependencies:
            None

    - Heartbeat logging (stop as string):
        Function:
            RPAConnection.log_heartbeat, RPAConnection.get_heartbeat
        Assertion:
            Heartbeat status is "STOPPED"
        Dependencies:
            None

    - Heartbeat logging (stop as boolean):
        Function:
            RPAConnection.log_heartbeat, RPAConnection.get_heartbeat
        Assertion:
            Heartbeat status is "STOPPED"
        Dependencies:
            None

    - Run heartbeat process:
        Function:
            External subprocess running heartbeat_worker.py
        Assertion:
            Heartbeat status is "RUNNING" and updates over time
        Dependencies:
            None

Requirements:
    - Database environment variable `TEST` must be configured
    - pyodbc must be installed and accessible
    - mbu_dev_shared_components must be available in PYTHONPATH
    - `heartbeat_worker.py` must exist in the `tests/` directory and be executable
    - `.venv/Scripts/python` must point to the correct Python interpreter
Further description:
    Each test uses the RPAConnection context manager to ensure proper handling of database transactions.
    COMMIT is set to False to test rollback behavior and avoid persistent changes to the test database.
    Heartbeat and logging tests validate time-sensitive operations with a threshold of 0.5 seconds.
    The heartbeat process test (`test_run_heartbeat`) runs a parallel subprocess to simulate real-time heartbeat updates.
"""

import socket
import subprocess
import time
from datetime import datetime, timedelta
from uuid import uuid4

import pyodbc
import pytest

from mbu_dev_shared_components.database.connection import RPAConnection

# Global test configuration
DB_ENV = "TEST"
COMMIT = False
THRES_SEC = 0.5


@pytest.mark.dependency()
def test_connection():
    """Test that RPAConnection successfully establishes a database connection

    Verifies that the `conn` and `cursor` attributes are initialized and not None
    after creating an instance of RPAConnection. Checks that cursor is closed afterwards.
    """
    with RPAConnection(db_env=DB_ENV, commit=COMMIT) as rpa_connection:
        # Assert connection is established
        assert rpa_connection.conn is not None
        assert rpa_connection.cursor is not None

    # Assert connection is closed
    with pytest.raises(
        pyodbc.ProgrammingError, match="Attempt to use a closed cursor."
    ):
        rpa_connection.get_constant("test_uuid")


@pytest.mark.dependency(depends=["test_connection"])
def test_add_get_constant():
    """
    Adds a test constant, rolls back the transaction.
    """
    test_constant_name = f"pytest_constant_{uuid4()}"
    test_value = "temporary_value"

    with RPAConnection(db_env=DB_ENV, commit=COMMIT) as rpa_connection:
        # Add constant (should be rolled back)
        rpa_connection.add_constant(test_constant_name, test_value, datetime.now())

        assert rpa_connection.cursor.rowcount == 1

        # Check that constant is added (will be rolled back after function)
        test_const = rpa_connection.get_constant(test_constant_name)

        assert test_const
        assert test_const["constant_name"] == test_constant_name
        assert test_const["value"] == test_value


@pytest.mark.dependency(depends=["test_connection"])
def test_add_get_credential():
    """
    Adds a test credential, rolls back the transaction.
    """
    test_credential_name = f"pytest_constant_{uuid4()}"
    test_username = "test_user"
    test_password = "test_password"

    with RPAConnection(db_env=DB_ENV, commit=COMMIT) as rpa_connection:
        # Add constant (should be rolled back)
        rpa_connection.add_credential(
            test_credential_name, test_username, test_password, datetime.now()
        )

        # Check that constant is added (will be rolled back after function)
        test_const = rpa_connection.get_credential(test_credential_name)

        assert test_const
        assert test_const["username"] == test_username
        assert test_const["decrypted_password"] == test_password


@pytest.mark.dependency(depends=["test_connection", "test_add_get_constant"])
def test_rollback():
    """
    Test that rollback undoes the insertion of a constant through the context manager.
    Asserts that a constant added in a scope without commiting to the db cannot be accessed outside the scope
    """
    test_constant_name = f"pytest_rollback_same_conn_{uuid4()}"
    test_value = "temporary_value"

    with RPAConnection(db_env=DB_ENV, commit=COMMIT) as rpa_connection:
        # Add constant
        rpa_connection.add_constant(test_constant_name, test_value, datetime.now())

    with RPAConnection(db_env=DB_ENV, commit=COMMIT) as rpa_connection:
        # Try to retrieve the constant in new connection
        with pytest.raises(
            ValueError, match=f"No constant found with name: {test_constant_name}"
        ):
            rpa_connection.get_constant(test_constant_name)


def test_log():
    """Test log functionality"""

    # Variables for test log row
    log_db = "journalizing.Journalize_log"
    level = "INFO"
    message = "test_log"
    context = "pytest"

    with RPAConnection(db_env=DB_ENV, commit=COMMIT) as rpa_connection:
        now = datetime.now()
        # Attempt insertion of log_event
        rpa_connection.log_event(
            log_db=log_db, level=level, message=message, context=context
        )
        # Assert that one row is inserted
        assert rpa_connection.cursor.rowcount == 1

        # Get latest log
        # pylint: disable-next=W0212
        log_row = rpa_connection.get_latest_log(log_db=log_db)[0]

        # Assert values of inserted element
        assert log_row[0] == level
        assert log_row[1] == message
        assert abs(log_row[2] - now) < timedelta(
            seconds=THRES_SEC
        )  # Latest log was within 0.1 second of start of function
        assert log_row[3] == context


def test_stop_heartbeat_str():
    """Test stopping heartbeat functionality"""

    servicename = "pytest"
    heartbeat_interval = 1.0
    details = "pytest testing heartbeat functionality"
    stop = "True"
    with RPAConnection(db_env=DB_ENV, commit=COMMIT) as rpa_connection:
        now = datetime.now()
        rpa_connection.log_heartbeat(
            stop=stop,
            servicename=servicename,
            heartbeat_interval=heartbeat_interval,
            details=details,
        )

        heartbeat = rpa_connection.get_heartbeat(service_name=servicename)[0]

        assert heartbeat[0] == servicename
        assert abs(heartbeat[1] - now) < timedelta(seconds=THRES_SEC)
        assert heartbeat[2] == "STOPPED"
        assert heartbeat[3] == socket.gethostname()


def test_stop_heartbeat_bool():
    """Test stopping heartbeat functionality"""

    servicename = "pytest"
    heartbeat_interval = 1.0
    details = "pytest testing heartbeat functionality"
    stop = True
    with RPAConnection(db_env=DB_ENV, commit=COMMIT) as rpa_connection:
        now = datetime.now()
        rpa_connection.log_heartbeat(
            stop=stop,
            servicename=servicename,
            heartbeat_interval=heartbeat_interval,
            details=details,
        )

        heartbeat = rpa_connection.get_heartbeat(service_name=servicename)[0]

        assert heartbeat[0] == servicename
        assert abs(heartbeat[1] - now) < timedelta(seconds=THRES_SEC)
        assert heartbeat[2] == "STOPPED"
        assert heartbeat[3] == socket.gethostname()


def test_run_heartbeat():
    """Test running heartbeat functionality
    Uses subprocess to run the heartbeat process in parallel and allows to stop it after some time
    Since we are using a stored procedure, we cannot roll back the transaction, so we have to accept the table being affected by the test
    Effectively we insert one row to the heartbeat table for the 'pytest' service
    """
    servicename = "pytest"
    heartbeat_interval = 2.0
    details = "pytest testing heartbeat functionality"
    stop = False
    now = datetime.now()
    heartbeat_process = subprocess.Popen(
        [
            ".venv/Scripts/python",
            "tests/heartbeat_worker.py",
            DB_ENV,
            str(stop),
            servicename,
            str(heartbeat_interval),
            details,
        ]
    )

    time.sleep(heartbeat_interval)

    with RPAConnection(db_env="TEST", commit=False) as rpa_connection:
        heartbeat = rpa_connection.get_heartbeat(servicename)[0]

        # Assert heartbeat is running and recent
        assert heartbeat[0] == servicename
        assert abs(heartbeat[1] - now) < timedelta(seconds=THRES_SEC)
        assert heartbeat[2] == "RUNNING"
        assert heartbeat[3] == socket.gethostname()

        # Test that heartbeat is updated by heartbeat interval time
        for i in range(5):
            print(f"Running assertion loop {i + 1}")
            prev_heartbeat_time = heartbeat[1]
            time.sleep(heartbeat_interval)
            # Get new heartbeat and assert that it is newer than previous hearbeat
            heartbeat = rpa_connection.get_heartbeat(servicename)[0]
            assert heartbeat[1] > prev_heartbeat_time, (
                f"Heartbeat not updated on iteration {i + 1}"
            )

    print("Should have finished assertion loop ")

    heartbeat_process.terminate()

    print("Should have terminated heartbeat process")

    with RPAConnection(db_env="TEST", commit=True) as rpa_connection:
        rpa_connection.log_heartbeat(
            stop=True,
            servicename=servicename,
            heartbeat_interval=2,
            details="Stop send from pytest",
        )


def test_execute_query():
    query = """
        SELECT
            *
        FROM
            [RPA].[rpa].[Constants]    
    """
    # Check that default SELECT query returns list
    with RPAConnection(db_env="TEST", commit=False) as rpa_conn:
        list_result = rpa_conn.execute_query(query=query)
    assert isinstance(list_result, list)
    # Check option to return dict
    with RPAConnection(db_env="TEST", commit=False) as rpa_conn:
        dict_result = rpa_conn.execute_query(query=query, return_dict=True)
    assert isinstance(dict_result, list)
    assert isinstance(dict_result[0], dict)
    # Check that returns have same length
    assert len(list_result) == len(dict_result)


if __name__ == "__main__":
    test_execute_query()
