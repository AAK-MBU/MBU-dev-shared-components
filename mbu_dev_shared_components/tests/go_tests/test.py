"""
Integration tests that hit the GetOrganized API.

Required environment variables:
    GO_API_ENDPOINT
    GO_USERNAME
    GO_PASSWORD

    TEST_PERSON_FULL_NAME
    TEST_PERSON_SSN
    TEST_PERSON_GO_ID
    TEST_PERSON_CITIZEN_CASE_ID
"""

import os
import xml.etree.ElementTree as ET

import pytest

from mbu_dev_shared_components.getorganized import contacts
from mbu_dev_shared_components.getorganized import cases
from mbu_dev_shared_components.getorganized import documents
from mbu_dev_shared_components.getorganized import objects


# --- Helper to load env vars safely ---
def _get_cfg(key: str) -> str:
    val = os.getenv(key)

    if not val:
        pytest.skip(f"env var '{key}' not set → skipping integration test")

    return val


# --- Load required config once ---
GO_API_ENDPOINT = _get_cfg("GO_API_ENDPOINT")
GO_USERNAME = _get_cfg("GO_API_USERNAME")
GO_PASSWORD = _get_cfg("GO_API_PASSWORD")

TEST_PERSON_FULL_NAME = _get_cfg("DADJ_FULL_NAME")
TEST_PERSON_SSN = _get_cfg("DADJ_SSN")
TEST_PERSON_GO_ID = _get_cfg("DADJ_GO_ID")
TEST_PERSON_CITIZEN_CASE_ID = _get_cfg("DADJ_BORGERMAPPE_SAGS_ID")


# ---------------------------------------------------------------------------
# tests
# ---------------------------------------------------------------------------
document_id = 14583373  # This value is tied to dadj profile

case_metadata_response = documents.get_document_metadata(
    api_endpoint=f"{GO_API_ENDPOINT}/_goapi/Documents/Metadata/{document_id}",
    api_username=GO_USERNAME,
    api_password=GO_PASSWORD,
)

parsed_metadata = ET.fromstring(case_metadata_response.json().get("Metadata")).attrib

print(f"Document Metadata: {parsed_metadata}")
