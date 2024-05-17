"""
This module provides a class for manipulating JSON objects by transforming lists
within the JSON into dictionaries with specified keys.

The primary class in this module is JSONManipulator, which contains methods for
converting lists associated with keys in a JSON object into dictionaries. This
is useful for restructuring JSON data into a more readable and accessible format.
"""
from typing import Any, Dict, Union


class JSONManipulator:
    """
    A class used to manipulate JSON objects.

    Methods
    -------
    transform_all_lists(json_obj: Dict[str, Any], key_map: Dict[str, List[str]]) -> Dict[str, Any]:
        Transforms all lists in the JSON object into dictionaries with specified keys.

    add_key_value_to_node(node: Union[Dict[str, Any], Any], key_value_pairs: Dict[str, Any]) -> None:
        Adds key-value pairs to a node in a JSON structure, supporting nested JSON structures.
    """

    @staticmethod
    def transform_all_lists(json_obj: Dict[str, Any], key_map: Dict[str, List[str]]) -> Dict[str, Any]:
        """
        Transforms all lists in the JSON object into dictionaries with specified keys.

        Parameters
        ----------
        json_obj : dict
            The JSON object to be manipulated.
        key_map : dict
            A dictionary where each key is a JSON key and the value is a list of keys to be used for the new dictionaries.

        Returns
        -------
        dict
            The updated JSON object with the transformed key-value pairs for all lists.
        """
        if not isinstance(json_obj, dict):
            raise TypeError("The input must be a dictionary.")

        def transform_lists(node: Any, key_map: Dict[str, List[str]]) -> Any:
            if isinstance(node, list):
                key = next((k for k, v in key_map.items() if len(v) == len(node)), None)
                if key:
                    return {key_map[key][j]: node[j] for j in range(len(key_map[key]))}
                else:
                    return node
            elif isinstance(node, dict):
                return {k: transform_lists(v, key_map) for k, v in node.items()}
            else:
                return node

        return transform_lists(json_obj, key_map)

    @staticmethod
    def add_key_value_to_node(node: Union[Dict[str, Any], Any], key_value_pairs: Dict[str, Any]) -> None:
        """
        Adds key-value pairs to a node in a JSON structure, supporting nested JSON structures.

        Parameters
        ----------
        node : Union[dict, any]
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

        def add_key_values(target: Union[Dict[str, Any], Any], pairs: Dict[str, Any]) -> None:
            """
            Recursively adds key-value pairs to the target JSON node.

            Parameters
            ----------
            target : Union[dict, any]
                The target JSON node to be manipulated.
            pairs : dict
                A dictionary of key-value pairs to be added to the target.
            """
            for key, value in pairs.items():
                if isinstance(value, dict):
                    if key not in target or not isinstance(target[key], dict):
                        target[key] = {}
                    add_key_values(target[key], value)
                else:
                    if isinstance(target, dict):
                        target[key] = value
                    else:
                        raise TypeError(f"Cannot assign key-value pair to non-dict target: {target}")

        add_key_values(node, key_value_pairs)
