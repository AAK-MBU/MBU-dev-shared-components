"""
Integration tests for MS Office / SharePoint functionality.

Env-vars required:
    SP_USERNAME
    SP_PASSWORD
    SP_SITE_URL
    SP_SITE_NAME
    SP_DOC_LIB
    SP_TEST_FOLDER
    SP_TEST_FILE       (a known Excel file uploaded to SP_TEST_FOLDER)
"""

# pylint: disable=W0102, R0912, W0621


import os

import datetime

import pytest

import openpyxl
from io import BytesIO

from mbu_dev_shared_components.msoffice365.sharepoint_api.files import Sharepoint
# from mbu_dev_shared_components.msoffice365.excel.excel_reader import ExcelReader

FOLDER_NAME = "MSOffice tests"


@pytest.fixture(scope="module")
def sharepoint_api():
    """Fixture to authenticate and return a SharePoint API instance."""

    def _get_cfg(key: str) -> str:
        val = os.getenv(key)

        if not val:
            pytest.skip(f"env var '{key}' not set → skipping")

        return val

    username = _get_cfg("SvcRpaMBU002_USERNAME")
    password = _get_cfg("SvcRpaMBU002_PASSWORD")

    site_url = "https://aarhuskommune.sharepoint.com"
    site_name = "MBURPA"
    document_library = "Delte dokumenter"

    sp = Sharepoint(username=username, password=password, site_url=site_url, site_name=site_name, document_library=document_library)

    assert sp.ctx is not None, "Authentication failed: ClientContext is None"

    return sp


# ---------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------
@pytest.mark.dependency(name="list_files")
def test_list_files_from_sharepoint_folder(sharepoint_api: Sharepoint):
    """
    Test function to test retrieval of a list of files in a specified SharePoint folder
    """

    files = sharepoint_api.fetch_files_list(FOLDER_NAME)

    assert isinstance(files, list), "Expected a list of files"

    file_names = [f["Name"] for f in files]

    assert "Test_Append_Rows.xlsx" in file_names, "Expected Test_Append_Rows.xlsx to be in list of files"


@pytest.mark.dependency(depends=["list_files"])
def test_append_row_to_excel(sharepoint_api: Sharepoint):
    """
    Test function to test function to append new rows to an existing Excel file
    """

    file_name = "Test_Append_Rows.xlsx"

    sheet_name = "Upload logs"

    headers = ["Upload date", "Upload time"]

    current_date = datetime.datetime.now().strftime("%d-%m-%Y")
    current_time = datetime.datetime.now().strftime("%H:%M")

    data = {
        "Upload date": current_date,
        "Upload time": current_time
    }

    sharepoint_api.append_row_to_sharepoint_excel(
        required_headers=headers,
        folder_name=FOLDER_NAME,
        excel_file_name=file_name,
        sheet_name=sheet_name,
        new_row=data,
    )

    # Step 2: Re-fetch and load the Excel file
    binary_file = sharepoint_api.fetch_file_using_open_binary(file_name, FOLDER_NAME)
    wb = openpyxl.load_workbook(BytesIO(binary_file))
    ws = wb[sheet_name]

    # Step 3: Read last non-header row
    all_rows = list(ws.iter_rows(values_only=True))

    newest_row = all_rows[-1]  # Index 1 = topmost after header

    assert newest_row[0] == current_date

    assert newest_row[1] == current_time
