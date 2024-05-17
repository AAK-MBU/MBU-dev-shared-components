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
    transform_all_lists(json_obj: List[Union[List[Any], Dict[str, Any]]], key_map: List[str]) -> List[Union[Dict[str, Any], Any]]:
        Transforms all lists in the JSON object into dictionaries with specified keys.

    add_key_value(json_obj: List[Union[List[Any], Dict[str, Any]]], keys: List[str], value: Any) -> List[Union[Dict[str, Any], Any]]:
        Adds a new key-value pair to the JSON object, supporting nested JSON structures.
    """

    @staticmethod
    def transform_all_lists(json_obj: List[Union[List[Any], Dict[str, Any]]], key_map: List[str]) -> List[Union[Dict[str, Any], Any]]:
        """
        Transforms all lists in the JSON object into dictionaries with specified keys.

        Parameters
        ----------
        json_obj : list
            The JSON object to be manipulated.
        key_map : list
            The list of keys to be used for the new dictionaries.

        Returns
        -------
        list
            The updated JSON object with the transformed key-value pairs for all lists.
        """
        if not isinstance(json_obj, list):
            raise TypeError("The input must be a list.")

        for i, item in enumerate(json_obj):
            if isinstance(item, list):
                if len(item) == len(key_map):
                    json_obj[i] = {key_map[j]: item[j] for j in range(len(key_map))}
                else:
                    raise ValueError(f"The length of the list at index {i} and the key_map must match.")
            elif isinstance(item, dict):
                JSONManipulator.transform_all_lists(list(item.values()), key_map)
        return json_obj

    @staticmethod
    def add_key_value(json_obj: List[Union[List[Any], Dict[str, Any]]], keys: List[str], value: Any) -> List[Union[Dict[str, Any], Any]]:
        """
        Adds a new key-value pair to the JSON object, supporting nested JSON structures.

        Parameters
        ----------
        json_obj : list
            The JSON object to be manipulated.
        keys : list
            The list of keys representing the path to where the value should be added.
        value : Any
            The value to be added.

        Returns
        -------
        list
            The updated JSON object with the new key-value pair added.
        """
        if not isinstance(json_obj, list):
            raise TypeError(f"The input must be a list. Received: {type(json_obj).__name__}")

        d = json_obj
        for key in keys[:-1]:
            found = False
            for item in d:
                if isinstance(item, dict) and key in item:
                    d = item[key]
                    found = True
                    break
            if not found:
                new_dict = {}
                d.append({key: new_dict})
                d = new_dict

        if isinstance(d, dict):
            d[keys[-1]] = value
        else:
            d.append({keys[-1]: value})

        return json_obj
