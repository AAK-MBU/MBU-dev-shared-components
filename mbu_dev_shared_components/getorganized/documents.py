"""This module..."""
from typing import Dict, Any
import requests
from mbu_dev_shared_components.getorganized.auth import get_ntlm_go_api_credentials


def upload_file_to_case(file_data: Dict[str, Any], api_endpoint: str, api_username: str, api_password: str) -> requests.Response:
    """
    Uploads a file to a case by sending file data as a JSON payload to a specific API endpoint.
    The function uses NTLM authentication and expects an environment variable for the API base URL.

    Parameters:
    file_data (Dict[str, Any]): A dictionary containing file data and associated case information to be uploaded.
    api_endpoint (str): GetOrganized API endpoint.
    api_username (str): The API username for GetOrganized API.
    api_password (str): The API password for GetOrganized API.

    Returns:
    requests.Response: The response object from the API.

    Raises:
    requests.RequestException: If the HTTP request fails for any reason.
    """
    headers = {'Content-Type': 'application/json'}
    response = requests.request(method='POST', url=api_endpoint, headers=headers, json=file_data, auth=get_ntlm_go_api_credentials(api_username, api_password), timeout=60)

    return response


def mark_file_as_case_record(documents_id: list, api_endpoint: str, api_username: str, api_password: str) -> Dict[str, Any]:
    """
    Marks one or more documents by their IDs as case records in the system via a POST request to a specific API endpoint.
    This operation modifies the status of the documents to reflect their new role as official case records.
    The function constructs the JSON payload by encapsulating the document IDs within a list under the 'DocumentIds' key.

    Parameters:
    documents_id (list): A list of integers representing document IDs that should be marked as case records.
    api_endpoint (str): GetOrganized API endpoint.
    api_username (str): The API username for GetOrganized API.
    api_password (str): The API password for GetOrganized API.

    Returns:
    Dict[str, Any]: The JSON response from the API, which includes the status of the operation and potentially updated document details.

    Raises:
    requests.RequestException: If the HTTP request fails for any reason.
    """
    headers = {'Content-Type': 'application/json'}
    payload = {"DocumentIds": documents_id}
    print(payload)
    response = requests.request(method='POST', url=api_endpoint, headers=headers, json=payload, auth=get_ntlm_go_api_credentials(api_username, api_password), timeout=60)

    return response.json()
