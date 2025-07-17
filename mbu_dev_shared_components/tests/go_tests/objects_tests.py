"""
Unit tests for data structure creation methods in CaseDataJson.
These are pure functions that return formatted dictionaries, used in API requests.

Should run on pull requests to ensure the data structure is correct.
"""

import pytest
from mbu_dev_shared_components.getorganized.objects import CaseDataJson


@pytest.fixture
def case_data_handler():
    """
    Fixture to provide an instance of CaseDataJson for testing.
    """
    return CaseDataJson()


def test_search_citizen_folder_data_json(case_data_handler: CaseDataJson):
    """
    Ensure that the search_citizen_folder_data_json method correctly builds
    a search structure for a citizen's full data and filters by 'Borgermappe' case category.
    """

    result = case_data_handler.search_citizen_folder_data_json(
        case_type_prefix="BOR",
        person_full_name="Test Person",
        person_id="12345",
        person_ssn="0101011234"
    )

    assert result["LogicalOperator"] == "AND"
    assert result["ExcludeDeletedCases"] == "True"
    assert result["ReturnCasesNumber"] == "1"

    assert {
        "InternalName": "ows_CCMContactData",
        "Value": "Test Person;#12345;#0101011234;#;#",
        "DataType": "Text",
        "ComparisonType": "Equal",
        "IsMultiValue": "False"
    } in result["FieldProperties"]

    assert {
        "InternalName": "ows_CaseCategory",
        "Value": "Borgermappe",
        "DataType": "Text",
        "ComparisonType": "Equal",
        "IsMultiValue": "False"
    } in result["FieldProperties"]


def test_generic_search_case_data_json_with_name_and_extra_field(case_data_handler: CaseDataJson):
    """
    Ensure that generic_search_case_data_json assembles a correct structure when using:
    - a custom case_type_prefix,
    - a non-default number of return cases,
    - full citizen data,
    - and extra field properties.
    """

    field_properties = {
        "ows_Title": "Lønbilag"
    }

    result = case_data_handler.generic_search_case_data_json(
        case_type_prefix="PER",
        person_full_name="Test Person",
        person_id="12345",
        person_ssn="0101011234",
        include_name=True,
        returned_cases_number="5",
        field_properties=field_properties
    )

    assert result["CaseTypePrefixes"] == ["PER"]

    assert {
        "InternalName": "ows_CCMContactData",
        "Value": "Test Person;#12345;#0101011234;#;#",
        "DataType": "Text",
        "ComparisonType": "Equal",
        "IsMultiValue": "False"
    } in result["FieldProperties"]

    assert result["ReturnCasesNumber"] == "5"

    assert {
        "InternalName": "ows_Title",
        "Value": "Lønbilag",
        "DataType": "Text",
        "ComparisonType": "Equal",
        "IsMultiValue": "False"
    } in result["FieldProperties"]


def test_generic_search_case_data_json_without_name(case_data_handler: CaseDataJson):
    """
    Ensure that generic_search_case_data_json builds correct contact data when include_name=False,
    and only includes one field (ows_CCMContactData) by default when no additional fields are passed.
    """

    result = case_data_handler.generic_search_case_data_json(
        case_type_prefix="BOR",
        person_full_name="Daniel Tester",
        person_id="12345",
        person_ssn="0101011234",
        include_name=False
    )

    assert result["CaseTypePrefixes"] == ["BOR"]

    assert {
        "InternalName": "ows_CCMContactData",
        "Value": ";#12345;#0101011234;#;#",
        "DataType": "Text",
        "ComparisonType": "Equal",
        "IsMultiValue": "False"
    } in result["FieldProperties"]

    assert result["ReturnCasesNumber"] == "1"

    assert len(result["FieldProperties"]) == 1
