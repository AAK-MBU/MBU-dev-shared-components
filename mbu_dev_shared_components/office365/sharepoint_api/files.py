"""This module defines a Sharepoint class that facilitates interactions with a SharePoint site.
It provides methods for authenticating with the site, listing files in a specified document
library folder, downloading files, and saving them to a local directory. The class is designed
to encapsulate all necessary functionalities for handling files on a SharePoint site, making it
suitable for scripts or applications that require automated access to SharePoint resources.

The Sharepoint class uses the Office365-REST-Python-Client library to communicate with SharePoint,
handling common tasks such as authentication, file retrieval, and file management. This includes
methods to authenticate users, fetch file lists from specific library folders, download individual
files, and save them locally. The class is initialized with user credentials and site details, which
are used throughout the class to manage SharePoint interactions.

Usage:
    After creating an instance of the Sharepoint class with the necessary credentials and site details,
    users can call methods to list files in a folder, download a specific file, or retrieve and save
    all files from a folder to a local directory. This makes it easy to integrate SharePoint file
    management into automated workflows or systems.

Example:
    sharepoint_details = {
        "username": "john@do.e",
        "password": "johndoe",
        "site_url": "https://site_url",
        "site_name": "department123",
        "document_library": "Shared documents"
    }
    sp = Sharepoint(**sharepoint_details)
    sp.get_files(sp, "FolderName", "C:\\LocalPath")

This module requires the `office365.sharepoint.client_context`, `office365.runtime.auth.user_credential`,
and `office365.sharepoint.files.file` modules from Office365-REST-Python-Client.
"""
from pathlib import PurePath
from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.files.file import File


class Sharepoint:
    """
    A class to interact with a SharePoint site, enabling authentication, file listing,
    downloading, and saving functionalities within a specified SharePoint document library.

    Attributes:
        username (str): Username for authentication.
        password (str): Password for authentication.
        site_url (str): URL of the SharePoint site.
        site_name (str): Name of the site.
        document_library (str): Document library path.
    """
    def __init__(self, username: str, password, site_url, site_name, document_library):
        """Initializes the Sharepoint class with credentials and site details.
        """
        self.username = username
        self.password = password
        self.site_url = site_url
        self.site_name = site_name
        self.document_library = document_library

    def _auth(self):
        """
        Authenticates to the SharePoint site and returns the client context.
        """
        try:
            conn = ClientContext(self.site_url).with_credentials(
                UserCredential(self.username, self.password)
            )
            return conn
        except Exception as e:
            print(f"Failed to authenticate: {e}")
            return None

    def fetch_files_list(self, folder_name: str) -> list:
        """
        Retrieve a list of files from a specified folder within the document library.

        This method authenticates the user and constructs the URL to the target folder using 
        the document library and folder name. It then attempts to retrieve and return the list 
        of files in the folder. If any errors occur during the process, an error message is 
        printed and an empty list is returned.

        Args:
            folder_name (str): The name of the folder within the document library from which to retrieve files.

        Returns:
            list: A list of file objects in the specified folder if the retrieval is successful, otherwise an empty list.
        """
        conn = self._auth()
        if conn:
            try:
                target_folder_url = f'{self.document_library}/{folder_name}'
                root_folder = conn.web.get_folder_by_server_relative_url(target_folder_url)
                root_folder.expand(["Files", "Folders"]).get().execute_query()
                return root_folder.files
            except Exception as e:
                print(f"Error retrieving files: {e}")
                return []
        return []

    def fetch_file_content(self, file_name: str, folder_name: str) -> bytes:
        """
        Download a file from a specified folder within the document library of the current site.

        This method authenticates the user, constructs the URL to the file using the site name, 
        document library, folder name, and file name. It then attempts to open and download 
        the file as binary. If successful, the binary content of the file is returned. If 
        any errors occur during the download process, an error message is printed and the 
        method returns None.

        Args:
            file_name (str): The name of the file to be downloaded.
            folder_name (str): The folder name where the file is stored.

        Returns:
            bytes: The binary content of the file if the download is successful, otherwise None.
        """
        conn = self._auth()
        if conn:
            try:
                file_url = f'/sites/{self.site_name}/{self.document_library}/{folder_name}/{file_name}'
                file_binary = File.open_binary(conn, file_url)
                return file_binary.content
            except Exception as e:
                print(f"Failed to download file: {e}")
                return None

    def _write_file(self, folder_destination: str, file_name: str, file_content: bytes) -> None:
        """
        Save the binary content of a file to a specified local destination.

        This method takes the binary content of a file and writes it to a file in the specified 
        local destination folder. The full path to the file is constructed using the destination 
        folder and the file name.

        Args:
            folder_destination (str): The local folder path where the file will be saved.
            file_name (str): The name of the file to be saved.
            file_content (bytes): The binary content of the file to be written to disk.

        Returns:
            None
        """
        file_directory_path = PurePath(folder_destination, file_name)
        with open(file_directory_path, 'wb') as file:
            file.write(file_content)

    def download_file(self, folder: str, filename: str, folder_destination: str) -> None:
        """
        Download a specified file from a specified folder and save it to a local destination.

        This method retrieves the specified file from the folder in the document library, 
        attempts to download it, and saves it to the specified local destination folder. 
        If the file cannot be downloaded, an error message is printed.

        Args:
            folder (str): The name of the folder in the document library from which to download the file.
            filename (str): The name of the file to download.
            folder_destination (str): The local folder path where the downloaded file will be saved.

        Returns:
            None
        """
        file_content = self.fetch_file_content(filename, folder)
        if file_content:
            self._write_file(folder_destination, filename, file_content)
        else:
            print(f"Failed to download {filename}")

    def download_files(self, folder: str, folder_destination: str) -> None:
        """
        Download all files from a specified folder and save them to a local destination.

        This method retrieves a list of files from the specified folder in the document library, 
        attempts to download each file, and saves it to the specified local destination folder. 
        If a file cannot be downloaded, an error message is printed, but the process continues 
        with the next file.

        Args:
            folder (str): The name of the folder in the document library from which to download files.
            folder_destination (str): The local folder path where the downloaded files will be saved.

        Returns:
            None
        """
        files_list = self.fetch_files_list(folder)
        for file in files_list:
            file_content = self.fetch_file_content(file.name, folder)
            if file_content:
                self._write_file(folder_destination, file.name, file_content)
            else:
                print(f"Failed to download {file.name}")
