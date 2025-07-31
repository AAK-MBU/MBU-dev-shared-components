"""
Integration tests that hit the GetOrganized API. Should run every morning?

Required environment variables:
    GO_API_ENDPOINT
    GO_USERNAME
    GO_PASSWORD
    DADJ_FULL_NAME
    DADJ_SSN
    DADJ_GO_ID
    DADJ_BORGERMAPPE_SAGS_ID
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


# --- Fixture that loads all config once ---
@pytest.fixture(scope="module")
def go_env():
    return {
        "endpoint": _get_cfg("GO_API_ENDPOINT"),
        "username": _get_cfg("GO_API_USERNAME"),
        "password": _get_cfg("GO_API_PASSWORD"),
        "full_name": _get_cfg("DADJ_FULL_NAME"),
        "ssn": _get_cfg("DADJ_SSN"),
        "go_id": _get_cfg("DADJ_GO_ID"),
        "case_id": _get_cfg("DADJ_BORGERMAPPE_SAGS_ID"),
    }


# ---------------------------------------------------------------------------
# Authentication test
# ---------------------------------------------------------------------------
def test_authentication_success(go_env):
    resp = contacts.contact_lookup(
        person_ssn=go_env["ssn"],
        api_endpoint=f"{go_env['endpoint']}/_goapi/contacts/readitem",
        api_username=go_env["username"],
        api_password=go_env["password"],
    )

    assert resp.status_code != 401
    assert resp.status_code != 403
    assert resp.ok


# ---------------------------------------------------------------------------
# Contact lookup test
# ---------------------------------------------------------------------------
def test_contact_lookup_returns_expected_name(go_env):
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


# ---------------------------------------------------------------------------
# Cases testing
# ---------------------------------------------------------------------------
def test_case_metadata_structure(go_env):
    resp = cases.get_case_metadata(
        api_endpoint=f"{go_env['endpoint']}/_goapi/Cases/Metadata/{go_env['case_id']}",
        api_username=go_env["username"],
        api_password=go_env["password"],
    )

    assert resp.ok
    resp_metadata_xml = resp.json().get("Metadata")
    assert resp_metadata_xml

    data = ET.fromstring(resp_metadata_xml).attrib

    assert data["ows_CaseID"] == go_env["case_id"]
    assert data["ows_CaseCategory"] == "Borgermappe"
    assert data["ows_CCMContactData"] == f"{go_env['full_name']};#{go_env['go_id']};#{go_env['ssn']};#;#"
    assert data["ows_CCMContactData_CPR"] == go_env["ssn"]


def test_find_case_by_case_properties(go_env):
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


# ---------------------------------------------------------------------------
# Documents testing
# ---------------------------------------------------------------------------
def test_get_document_metadata(go_env):
    document_id = 14583373  # tied to this profile

    resp = documents.get_document_metadata(
        api_endpoint=f"{go_env['endpoint']}/_goapi/Documents/Metadata/{document_id}",
        api_username=go_env["username"],
        api_password=go_env["password"],
    )

    assert resp.ok
    data = ET.fromstring(resp.json().get("Metadata")).attrib

    assert "ows_Title" in data


def test_search_documents(go_env):
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
    search_term = f"{go_env['full_name']} {go_env['ssn']}"

    # 1. No date range
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

    # 2. With date range
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
