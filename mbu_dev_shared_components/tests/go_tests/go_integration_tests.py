"""
Integration tests that hit the GetOrganized API. Should run every morning?

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

import requests

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

# Below values are tied to the dadj profile
TEST_PERSON_FULL_NAME = _get_cfg("DADJ_FULL_NAME")
TEST_PERSON_SSN = _get_cfg("DADJ_SSN")
TEST_PERSON_GO_ID = _get_cfg("DADJ_GO_ID")
TEST_PERSON_CITIZEN_CASE_ID = _get_cfg("DADJ_BORGERMAPPE_SAGS_ID")


# ---------------------------------------------------------------------------
# Authentication test
# ---------------------------------------------------------------------------
def test_authentication_success():
    """Ensure valid credentials return authorized access (not 401/403)."""

    resp = contacts.contact_lookup(
        person_ssn=TEST_PERSON_SSN,
        api_endpoint=f"{GO_API_ENDPOINT}/_goapi/contacts/readitem",
        api_username=GO_USERNAME,
        api_password=GO_PASSWORD,
    )

    assert resp.status_code != 401, "Unauthorized - check username/password"

    assert resp.status_code != 403, "Forbidden - credentials lack permissions"

    assert resp.ok, f"Unexpected failure - status={resp.status_code}"


# ---------------------------------------------------------------------------
# Contact lookup test
# ---------------------------------------------------------------------------
def test_contact_lookup_returns_expected_name():
    """
    Ensure contact_lookup returns JSON with expected fields and matches
    the known test citizen.
    """

    resp = contacts.contact_lookup(
        person_ssn=TEST_PERSON_SSN,
        api_endpoint=f"{GO_API_ENDPOINT}/_goapi/contacts/readitem",
        api_username=GO_USERNAME,
        api_password=GO_PASSWORD,
    )

    assert resp.ok, f"Contact lookup failed, status={resp.status_code}"

    data = resp.json()

    assert data["FullName"] == TEST_PERSON_FULL_NAME

    assert data["ID"] == TEST_PERSON_GO_ID

    assert data["CPR"] == TEST_PERSON_SSN


# ---------------------------------------------------------------------------
# Cases testing
# ---------------------------------------------------------------------------
def test_case_metadata_structure():
    """
    Fetch metadata for a known case and check that returned 'Metadata' XML
    parses and contains expected root attributes.
    """

    resp = cases.get_case_metadata(
        api_endpoint=f"{GO_API_ENDPOINT}/_goapi/Cases/Metadata/{TEST_PERSON_CITIZEN_CASE_ID}",
        api_username=GO_USERNAME,
        api_password=GO_PASSWORD,
    )

    assert resp.ok, f"Metadata request failed, status={resp.status_code}"

    resp_metadata_xml = resp.json().get("Metadata")

    assert resp_metadata_xml, "No 'Metadata' field in response"

    data = ET.fromstring(resp_metadata_xml).attrib

    assert data["ows_CaseID"] == TEST_PERSON_CITIZEN_CASE_ID

    assert data["ows_CaseCategory"] == "Borgermappe"

    assert data["ows_CCMContactData"] == f"{TEST_PERSON_FULL_NAME};#{TEST_PERSON_GO_ID};#{TEST_PERSON_SSN};#;#"

    assert data["ows_CCMContactData_CPR"] == TEST_PERSON_SSN


def test_find_case_by_case_properties():
    """
    Test searching for a case by its properties using the find_case_by_case_properties function.
    This should return a response with the expected case metadata.
    """

    case_data_json = objects.CaseDataJson()

    case_data = case_data_json.search_citizen_folder_data_json(
        case_type_prefix="BOR",
        person_full_name=TEST_PERSON_FULL_NAME,
        person_id=TEST_PERSON_GO_ID,
        person_ssn=TEST_PERSON_SSN
    )

    resp = cases.find_case_by_case_properties(
        case_data=case_data,
        api_endpoint=f"{GO_API_ENDPOINT}/_goapi/Cases/FindByCaseProperties",
        api_username=GO_USERNAME,
        api_password=GO_PASSWORD,
    )

    assert resp.ok, f"Case search failed, status={resp.status_code}"

    data = resp.json().get("CasesInfo")

    assert isinstance(data, list), f"Expected a list of cases, actual returned type: {type(data)}"

    assert len(data) == 1, f"Expected one case to be returned, actual returned cases: {len(data)}"

    assert data[0].get("CaseID") == TEST_PERSON_CITIZEN_CASE_ID, f"Returned case ID does not match expected, actual returned case_id: {data[0].get('CaseID')}"


# ---------------------------------------------------------------------------
# Documents testing
# ---------------------------------------------------------------------------
def test_get_document_metadata():
    """
    Test fetching metadata for a document by its ID.
    This should return a response with the expected document metadata.
    """

    document_id = 14583373  # This value is tied to dadj profile

    resp = documents.get_document_metadata(
        api_endpoint=f"{GO_API_ENDPOINT}/_goapi/Documents/Metadata/{document_id}",
        api_username=GO_USERNAME,
        api_password=GO_PASSWORD,
    )

    assert resp.ok, f"Document metadata request failed, status={resp.status_code}"

    data = ET.fromstring(resp.json().get("Metadata")).attrib

    assert "ows_Title" in data, "Metadata does not contain 'ows_Title'"


def test_search_documents():
    """
    Test searching for documents by their properties.
    This should return a response with the expected document metadata.
    """

    search_term = f"{TEST_PERSON_FULL_NAME} {TEST_PERSON_SSN}"

    resp = documents.search_documents(
        search_term=search_term,
        api_endpoint=f"{GO_API_ENDPOINT}/_goapi/Search/Results",
        api_username=GO_USERNAME,
        api_password=GO_PASSWORD,
    )

    assert resp.ok, f"Document search failed, status={resp.status_code}"

    results = resp.json().get("Rows").get("Results")

    total_rows = resp.json().get("TotalRows")

    assert isinstance(results, list), f"Expected a list of documents, actual returned type: {type(results)}"

    if total_rows == 0:
        assert len(results) == 0, "Expected no documents to be returned, but some were found"

    else:
        assert len(results) > 0, "Expected at least one document to be returned, but none were found"

        assert len(results) == total_rows, f"Expected {total_rows} documents, but found {len(results)}"

        for doc in results:
            assert "title" in doc, "Document metadata does not contain 'title'"

            assert "created" in doc, "Document metadata does not contain 'created'"

            assert "caseid" in doc, "Document metadata does not contain 'caseid'"


def _validate_modern_search_response(resp: requests.Response):
    """
    Shared logic to validate a modern search response.
    """

    assert resp.ok, f"Modern search failed, status={resp.status_code}"

    json_data = resp.json()

    results = json_data.get("results", {}).get("Results", [])

    total_rows = json_data.get("totalRows")

    assert isinstance(results, list), f"Expected list, got {type(results)}"

    if total_rows == 0:
        assert len(results) == 0, "Expected no results, but some were found"

    else:
        assert len(results) > 0, "Expected results, but none found"

        assert len(results) == total_rows, f"Expected {total_rows}, got {len(results)}"

        for doc in results:
            assert "title" in doc, "Missing 'title' in result"

            assert "created" in doc, "Missing 'created' in result"

            assert "caseid" in doc, "Missing 'caseid' in result"


def test_modern_search():
    """
    Test modern search with and without date range.
    """

    search_term = f"{TEST_PERSON_FULL_NAME} {TEST_PERSON_SSN}"

    # 1: No date range
    resp_1 = documents.modern_search(
        page_index=0,
        search_term=search_term,
        start_date=None,
        end_date=None,
        only_items=False,
        case_type_prefix="BOR",
        api_endpoint=f"{GO_API_ENDPOINT}/_goapi/search/ExecuteModernSearch",
        api_username=GO_USERNAME,
        api_password=GO_PASSWORD,
    )

    # 2: With date range
    resp_2 = documents.modern_search(
        page_index=0,
        search_term=search_term,
        start_date="2025-03-01",
        end_date="2025-03-31",
        only_items=False,
        case_type_prefix="BOR",
        api_endpoint=f"{GO_API_ENDPOINT}/_goapi/search/ExecuteModernSearch",
        api_username=GO_USERNAME,
        api_password=GO_PASSWORD,
    )

    _validate_modern_search_response(resp_1)

    _validate_modern_search_response(resp_2)
