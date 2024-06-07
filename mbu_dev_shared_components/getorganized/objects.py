"""This module contains classes relating data to be used in api request to
GetOrganized when working with cases and documents."""
import json
from typing import Literal


CaseTypePrefix = Literal["BOR", "EMN", "PPR", "AKT", "ELM", "PER", "GEO", "SAM", "MOD"]


class CaseDataJson:
    """
    A class responsible for creating JSON representations of case data structures for different types of cases.

    This class provides a method to serialize case data into a JSON format.
    """
    def case_data_json(self, case_type_prefix: CaseTypePrefix, metadata_xml: str, return_when_case_fully_created: bool) -> str:
        """
        Creates a JSON string representing a case with the provided attributes.

        Parameters:
        case_type_prefix (CaseTypePrefix): The prefix indicating the type of the case. Must be one of the predefined literal values.
        metadata_xml (str): XML-formatted string containing metadata associated with the case.
        return_when_case_fully_created (bool): A flag indicating whether to wait for the case to be fully created before returning.

        Returns:
        str: A JSON formatted string representing the case with the specified attributes, ensuring non-ASCII characters are retained and output is indented for readability.
        """
        case_data = {
            "CaseTypePrefix": case_type_prefix,
            "MetadataXml": metadata_xml,
            "ReturnWhenCaseFullyCreated": return_when_case_fully_created
        }
        return json.dumps(case_data, ensure_ascii=False, indent=4)

    def search_case_folder_data_json(self, metadata_xml: str) -> str:
        """
        Creates a JSON string representing a search string for case folder with the provided attributes.

        Parameters:
        case_type_prefix (CaseTypePrefix): The prefix indicating the type of the case. Must be one of the predefined literal values.
        metadata_xml (str): XML-formatted string containing metadata associated with the case.

        Returns:
        str: A JSON formatted string representing the case with the specified attributes, ensuring non-ASCII characters are retained and output is indented for readability.
        """
        search_case_folder_data = {
            "MetadataXml": metadata_xml,
        }
        return json.dumps(search_case_folder_data, ensure_ascii=False, indent=4)

class DocumentJsonCreator:
    """
    A class responsible for creating JSON representations of document data structures
    associated with a specific case.

    This class is used to serialize document attributes into a JSON format.
    """
    def document_data_json(self, case_id: str, list_name: str, folder_path: str, filename: str, metadata: str, overwrite: bool, data_in_bytes: bytes) -> str:
        """
        Creates a JSON string representing a document with the provided attributes.

        Parameters:
        case_id (str): The unique identifier of the case to which the document is related.
        list_name (str): The name of the list within the case where the document is stored.
        folder_path (str): The directory path where the document is located on the case.
        filename (str): The name of the file including its extension.
        metadata (str): XML-formatted string containing metadata associated with the document.
        overwrite (bool): A flag indicating whether the existing file should be overwritten if it exists.
        data_in_bytes (bytes): The binary data of the file being represented.

        Returns:
        str: A JSON formatted string representing the document with specified attributes, ensuring non-ASCII characters are retained and output is indented for readability.
        """
        document_data = {
            "CaseId": case_id,
            "ListName": list_name,
            "FolderPath": folder_path,
            "FileName": filename,
            "Metadata": metadata,
            "Overwrite": overwrite,
            "Bytes": data_in_bytes
        }
        return json.dumps(document_data, ensure_ascii=False, indent=4)
