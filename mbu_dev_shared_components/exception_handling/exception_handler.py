"""This module contains various functions and classes to handle errors in the framework."""

import json
import traceback

from OpenOrchestrator.database.queues import QueueElement, QueueStatus
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection

from mbu_dev_shared_components.exception_handling import error_screenshot, incident_handler


class BusinessError(Exception):
    """An empty exception used to identify errors caused by breaking business rules"""


def handle_error(message: str, error_count: str | None, error: Exception, queue_element: QueueElement | None, orchestrator_connection: OrchestratorConnection, smtp_server) -> None:
    """Handles an error caught during the process.
    Logs an error to OpenOrchestrator.
    Marks the queue element (if any) as failed.
    Sends an error screenshot by email.

    Args:
        message: A message to prepend to the error message.
        error: The exception that should be handled.
        queue_element: The queue element to fail, if any.
        orchestrator_connection: A connection to OpenOrchestrator.
    """
    error_dict = {
        "type": message,
        "error_count": error_count,
        "message": str(error),
        "trace": traceback.format_exc()
    }
    error_msg = json.dumps(error_dict, ensure_ascii=False)
    error_email = "Error Email"

    orchestrator_connection.log_error(error_msg)
    if queue_element:
        orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.FAILED, error_msg)

    error_screenshot.send_error_screenshot(error_email, error, orchestrator_connection.process_name, smtp_server)

    if "process" in message.lower():
        incident_handler.post_incident(message=message, error=error, queue_element=queue_element)


def log_exception(orchestrator_connection: OrchestratorConnection) -> callable:
    """Creates a function to be used as an exception hook that logs any uncaught exception in OpenOrchestrator.

    Args:
        orchestrator_connection: The connection to OpenOrchestrator.

    Returns:
        callable: A function that can be assigned to sys.excepthook.
    """
    def inner(exception_type, value, traceback_string):
        orchestrator_connection.log_error(f"Uncaught Exception:\nType: {exception_type}\nValue: {value}\nTrace: {traceback_string}")
    return inner
