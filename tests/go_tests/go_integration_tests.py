"""
Integration tests for the GetOrganized API.

These tests validate the following key functionalities:
1. Authentication success using CPR lookup
2. Contact lookup returns correct citizen profile
3. Retrieval of metadata for a specific case (Borgermappe)
4. Case lookup using case properties
5. Document metadata retrieval
6. Document search (legacy and modern search APIs)

Expected to run daily to ensure API stability and data consistency.

Required environment variables:
- GO_API_ENDPOINT:        Base URL for GetOrganized API
- GO_API_USERNAME:        API username for authentication
- GO_API_PASSWORD:        API password
- DADJ_FULL_NAME:         Full name of test citizen
- DADJ_SSN:               CPR number of test citizen
- DADJ_GO_ID:             Internal ID of test citizen in GO
- DADJ_BORGERMAPPE_SAGS_ID: Case ID of the test citizen's "Borgermappe"
"""

import os
import xml.etree.ElementTree as ET
import requests
import pytest

from mbu_dev_shared_components.getorganized import contacts
from mbu_dev_shared_components.getorganized import cases
from mbu_dev_shared_components.getorganized import documents
from mbu_dev_shared_components.getorganized import objects


# -------------------------------
# Helper to load environment vars safely
# -------------------------------
def _get_cfg(key: str) -> str:
    val = os.getenv(key)

    if not val:
        pytest.skip(f"env var '{key}' not set → skipping integration test")

    return val


@pytest.fixture(scope="module")
def go_env():
    """
    Loads required environment variables for the GetOrganized API tests.
    Skips tests if any required variable is missing.
    """

    return {
        "endpoint": _get_cfg("GO_API_ENDPOINT"),
        "username": _get_cfg("GO_API_USERNAME"),
        "password": _get_cfg("GO_API_PASSWORD"),
        "full_name": _get_cfg("DADJ_FULL_NAME"),
        "ssn": _get_cfg("DADJ_SSN"),
        "go_id": _get_cfg("DADJ_GO_ID"),
        "case_id": _get_cfg("DADJ_BORGERMAPPE_SAGS_ID"),
    }


def test_authentication_success(go_env):
    """
    Ensures valid credentials can access the API without 401/403.
    """

    resp = contacts.contact_lookup(
        person_ssn=go_env["ssn"],
        api_endpoint=f"{go_env['endpoint']}/_goapi/contacts/readitem",
        api_username=go_env["username"],
        api_password=go_env["password"],
    )

    assert resp.status_code != 401
    assert resp.status_code != 403
    assert resp.ok


def test_contact_lookup_returns_expected_name(go_env):
    """
    Verifies that contact lookup returns correct full name, ID, and CPR.
    """

    resp = contacts.contact_lookup(
        person_ssn=go_env["ssn"],
        api_endpoint=f"{go_env['endpoint']}/_goapi/contacts/readitem",
        api_username=go_env["username"],
        api_password=go_env["password"],
    )

    assert resp.ok

    data = resp.json()

    assert data["FullName"] == go_env["full_name"]
    assert data["ID"] == go_env["go_id"]
    assert data["CPR"] == go_env["ssn"]


def test_case_metadata_structure(go_env):
    """
    Validates the metadata structure of a known 'Borgermappe' case.
    """

    resp = cases.get_case_metadata(
        api_endpoint=f"{go_env['endpoint']}/_goapi/Cases/Metadata/{go_env['case_id']}",
        api_username=go_env["username"],
        api_password=go_env["password"],
    )

    assert resp.ok

    # Extract XML metadata and parse attributes
    resp_metadata_xml = resp.json().get("Metadata")

    assert resp_metadata_xml

    data = ET.fromstring(resp_metadata_xml).attrib

    assert data["ows_CaseID"] == go_env["case_id"]

    assert data["ows_CaseCategory"] == "Borgermappe"

    assert data["ows_CCMContactData"] == f"{go_env['full_name']};#{go_env['go_id']};#{go_env['ssn']};#;#"

    assert data["ows_CCMContactData_CPR"] == go_env["ssn"]


def test_find_case_by_case_properties(go_env):
    """
    Searches for a case using known properties of the test citizen.
    """

    case_data_json = objects.CaseDataJson()

    case_data = case_data_json.search_citizen_folder_data_json(
        case_type_prefix="BOR",
        person_full_name=go_env["full_name"],
        person_id=go_env["go_id"],
        person_ssn=go_env["ssn"]
    )

    resp = cases.find_case_by_case_properties(
        case_data=case_data,
        api_endpoint=f"{go_env['endpoint']}/_goapi/Cases/FindByCaseProperties",
        api_username=go_env["username"],
        api_password=go_env["password"],
    )

    assert resp.ok

    data = resp.json().get("CasesInfo")

    assert isinstance(data, list)

    assert len(data) == 1

    assert data[0].get("CaseID") == go_env["case_id"]


def test_get_document_metadata(go_env):
    """
    Fetches metadata for a known document tied to the test citizen.
    """
    document_id = 14583373  # ID must be valid for test profile

    resp = documents.get_document_metadata(
        api_endpoint=f"{go_env['endpoint']}/_goapi/Documents/Metadata/{document_id}",
        api_username=go_env["username"],
        api_password=go_env["password"],
    )

    assert resp.ok

    data = ET.fromstring(resp.json().get("Metadata")).attrib

    assert "ows_Title" in data


def test_search_documents(go_env):
    """
    Performs a legacy document search using full name + CPR.
    """

    search_term = f"{go_env['full_name']} {go_env['ssn']}"

    resp = documents.search_documents(
        search_term=search_term,
        api_endpoint=f"{go_env['endpoint']}/_goapi/Search/Results",
        api_username=go_env["username"],
        api_password=go_env["password"],
    )

    assert resp.ok

    results = resp.json().get("Rows").get("Results")
    total_rows = resp.json().get("TotalRows")

    assert isinstance(results, list)

    if total_rows == 0:
        assert len(results) == 0

    else:
        assert len(results) == total_rows

        for doc in results:
            assert "title" in doc
            assert "created" in doc
            assert "caseid" in doc


def _validate_modern_search_response(resp: requests.Response):
    """
    Helper: Validates structure of modern search response.
    """

    assert resp.ok

    json_data = resp.json()

    results = json_data.get("results", {}).get("Results", [])

    total_rows = json_data.get("totalRows")

    assert isinstance(results, list)

    if total_rows == 0:
        assert len(results) == 0

    else:
        assert len(results) == total_rows
        for doc in results:

            assert "title" in doc
            assert "created" in doc
            assert "caseid" in doc


def test_modern_search(go_env):
    """
    Runs two modern searches: one without date filter, one with date filter.
    """

    search_term = f"{go_env['full_name']} {go_env['ssn']}"

    # Search 1: All-time
    resp_1 = documents.modern_search(
        page_index=0,
        search_term=search_term,
        start_date=None,
        end_date=None,
        only_items=False,
        case_type_prefix="BOR",
        api_endpoint=f"{go_env['endpoint']}/_goapi/search/ExecuteModernSearch",
        api_username=go_env["username"],
        api_password=go_env["password"],
    )

    # Search 2: Specific March 2025 range
    resp_2 = documents.modern_search(
        page_index=0,
        search_term=search_term,
        start_date="2025-03-01",
        end_date="2025-03-31",
        only_items=False,
        case_type_prefix="BOR",
        api_endpoint=f"{go_env['endpoint']}/_goapi/search/ExecuteModernSearch",
        api_username=go_env["username"],
        api_password=go_env["password"],
    )

    _validate_modern_search_response(resp_1)

    _validate_modern_search_response(resp_2)
