"""This module contains functionality to authenticate and health check GetOrganized api."""

import requests
from mbu_dev_shared_components.getorganized.auth import get_ntlm_go_api_credentials


def health_check(api_endpoint: str, api_username: str, api_password: str) -> bool:
    """Sends a GET request to check whether the API is running.

    To be used before starting a processing that requires the GO API,
    such that errors caused by the API being down can be registered.
    """
    response = requests.request(
        method="GET",
        url=api_endpoint,
        auth=get_ntlm_go_api_credentials(api_username, api_password),
        timeout=60,
    )

    # Return True if response is ok, else return False
    return response.ok
