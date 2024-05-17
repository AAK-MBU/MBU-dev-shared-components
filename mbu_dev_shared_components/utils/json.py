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

    add_key_value_to_node(node: Union[Dict[str, Any], List[Any]], key_value_pairs: Dict[str, Any]) -> None:
        Adds key-value pairs to a node in a JSON structure, supporting nested JSON structures.
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
    def add_key_value_to_node(node: Union[Dict[str, Any], List[Any]], key_value_pairs: Dict[str, Any]) -> None:
        """
        Adds key-value pairs to a node in a JSON structure, supporting nested JSON structures.

        Parameters
        ----------
        node : Union[dict, list]
            The JSON node to be manipulated.
        key_value_pairs : dict
            A dictionary of key-value pairs to be added to the node.

        Example
        -------
        >>> json_data = {"name": "John Doe"}
        >>> key_value_pairs = {"institution_number": "1234", "nested": {"key": "value"}}
        >>> JSONManipulator.add_key_value_to_node(json_data, key_value_pairs)
        >>> print(json.dumps(json_data, indent=4))
        {
            "name": "John Doe",
            "institution_number": "1234",
            "nested": {
                "key": "value"
            }
        }
        """
        def add_key_values(target: Union[Dict[str, Any], List[Any]], pairs: Dict[str, Any]) -> None:
            """
            Recursively adds key-value pairs to the target JSON node.

            Parameters
            ----------
            target : Union[dict, list]
                The target JSON node to be manipulated.
            pairs : dict
                A dictionary of key-value pairs to be added to the target.
            """
            for key, value in pairs.items():
                if isinstance(value, dict):
                    if isinstance(target, list):
                        for item in target:
                            if isinstance(item, dict) and key in item:
                                add_key_values(item[key], value)
                            elif isinstance(item, dict):
                                item[key] = {}
                                add_key_values(item[key], value)
                    else:
                        if key not in target or not isinstance(target[key], dict):
                            target[key] = {}
                        add_key_values(target[key], value)
                else:
                    if isinstance(target, list):
                        for item in target:
                            if isinstance(item, dict):
                                item[key] = value
                    else:
                        target[key] = value

        add_key_values(node, key_value_pairs)
