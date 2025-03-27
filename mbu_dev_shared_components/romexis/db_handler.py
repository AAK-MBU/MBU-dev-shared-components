"""
This module contains the RomexisDbHandler class,
which handles database operations related to the Romexis system.
"""

import pyodbc


class RomexisDbHandler:
    """Handles database operations related to the Romexis system."""

    def __init__(self, conn_str: str):
        """
        Initializes the database instance.

        Args:
            conn_str (str): Connection string to the database.
        """
        self.connection_string = conn_str

    def _execute_query(self, query: str, params: tuple):
        """
        Executes a SQL query with parameters and returns the results as a list of dictionaries.

        Args:
            query (str): The SQL query to execute.
            params (tuple): The parameters for the SQL query.

        Returns:
            list: A list of dictionaries, where each dictionary represents a row from the query result.
        """
        conn = pyodbc.connect(self.connection_string)
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        columns = [column[0] for column in cursor.description]

        result = [dict(zip(columns, row)) for row in rows]

        return result

    def get_person_data(self, external_id: str) -> list:
        """
        Gets person data from the database.

        Returns:
            list: A list of dictionaries, where each dictionary represents a person.
        """
        query = """
            SELECT
                [person_id],
                [external_id],
                [first_name],
                [second_name],
                [third_name],
                [last_name],
                [date_of_birth]
            FROM
                [Romexis_db].[dbo].[RRM_Person]
            WHERE
                [external_id] = ?
        """

        return self._execute_query(query, (external_id,))

    def get_image_ids(self, patient_id: int) -> list:
        """
        Gets image ids from the database.

        Returns:
            list: A list of dictionaries, where each dictionary represents an image id.
        """
        query = """
            SELECT
                [image_id]
            FROM
                [Romexis_db].[dbo].[RIM_Image_Info]
            WHERE
                [patient_id] = ?
        """

        rows = self._execute_query(query, (patient_id,))

        return [row["image_id"] for row in rows]

    def get_image_data(self, image_ids: list) -> list:
        """
        Gets image data from the database.

        image_type 1 = Panorama
        image_type 2 = Cephalostat
        image_type 3 = interoralt
        image_type 4 = foto

        Returns:
            list: A list of dictionaries, where each dictionary represents an image.
        """

        placeholders = ", ".join(["?"] * len(image_ids))

        query = f"""
            SELECT
                [person_id],
                [first_name],
                [last_name],
                [date_of_birth],
                [gender],
                [external_id],
                [doctor_id],
                rii.[image_id],
                [image_size],
                [image_date],
                [image_time],
                [image_source],
                [image_type],
                [image_subtype],
                [image_format],
                [bit_depth],
                [pixel_size],
                [rotation_angle],
                [is_mirrored],
                [tooth_mask],
                [tooth_mask_child],
                [operator_id],
                [string_value] AS [file_path]
            FROM
                [Romexis_db].[dbo].[RIM_Image_Info] rii
            INNER JOIN [romexis_db].[dbo].[RRM_Person] rp
                ON rii.patient_id = rp.person_id
            INNER JOIN [Romexis_db].[dbo].[RIM_Image_Attrib] ria
                ON ria.image_id = rii.image_id AND ria.attrib_type = 1
            WHERE
                rii.[image_id] IN ({placeholders})
                AND rii.[image_type] IN (1, 2, 3, 4)
        """

        return self._execute_query(query, tuple(image_ids))
