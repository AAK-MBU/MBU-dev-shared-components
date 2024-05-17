"""
This module provides a class for manipulating JSON objects by transforming lists
within the JSON into dictionaries with specified keys.

The primary class in this module is JSONManipulator, which contains methods for
converting lists associated with keys in a JSON object into dictionaries. This
is useful for restructuring JSON data into a more readable and accessible format.
"""
from typing import Any, Dict, List, Union


class JSONManipulator:
    """
    A class used to manipulate JSON objects.

    Methods
    -------
    transform_all_lists(json_obj: Dict[str, Union[List[Any], Dict[str, Any]]], key_map: List[str]) -> Dict[str, Dict[str, Any]]:
        Transforms all lists in the JSON object into dictionaries with specified keys.

    add_key_value(json_obj: Dict[str, Any], keys: List[str], value: Any) -> Dict[str, Any]:
        Adds a new key-value pair to the JSON object, supporting nested JSON structures.
    """

    @staticmethod
    def transform_all_lists(json_obj: Dict[str, Union[List[Any], Dict[str, Any]]], key_map: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        Transforms all lists in the JSON object into dictionaries with specified keys.

        Parameters
        ----------
        json_obj : dict
            The JSON object to be manipulated.
        key_map : list
            The list of keys to be used for the new dictionaries.

        Returns
        -------
        dict
            The updated JSON object with the transformed key-value pairs for all lists.
        """
        if not isinstance(json_obj, dict):
            raise TypeError("The input must be a dictionary.")

        for key, value in json_obj.items():
            if isinstance(value, list):
                if len(value) == len(key_map):
                    json_obj[key] = {key_map[i]: value[i] for i in range(len(key_map))}
                else:
                    raise ValueError(f"The length of the list for key '{key}' and the key_map must match.")
            else:
                raise TypeError(f"The value for key '{key}' is not a list.")
        return json_obj

    @staticmethod
    def add_key_value(json_obj: Dict[str, Any], keys: List[str], value: Any) -> Dict[str, Any]:
        """
        Adds a new key-value pair to the JSON object, supporting nested JSON structures.

        Parameters
        ----------
        json_obj : dict
            The JSON object to be manipulated.
        keys : list
            The list of keys representing the path to where the value should be added.
        value : Any
            The value to be added.

        Returns
        -------
        dict
            The updated JSON object with the new key-value pair added.
        """
        if not isinstance(json_obj, dict):
            raise TypeError(f"The input must be a dictionary. Received: {type(json_obj).__name__}")

        d = json_obj
        for key in keys[:-1]:
            if key not in d or not isinstance(d[key], dict):
                d[key] = {}
            d = d[key]

        d[keys[-1]] = value
        return json_obj
