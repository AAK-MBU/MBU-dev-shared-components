"""This module contains the PatientHandler class, which manages patient-related actions in the Solteq Tand application."""
import os
import uiautomation as auto

from .base_ui import BaseUI


class SolteqTandApp(BaseUI):
    """
    Main application handler for Solteq Tand, integrating various components.
    Inherits from BaseUI for core UI methods, and composes all feature handlers.
    """

    def __init__(self, app_path: str, username: str = None, password: str = None):
        """
        Initializes the Solteq Tand application handler.
        Args:
            app_path (str): Path to the Solteq Tand application executable.
            username (str): Username for login.
            password (str): Password for login.
        """
        super().__init__()
        self.app_path = app_path
        self.username = username
        self.password = password
        self.app_window = None

        # Compose feature handlers, passing this App as parent
        from .patient import PatientHandler
        from .appointment import AppointmentHandler
        from .document import DocumentHandler
        from .edi_portal import EDIHandler
        from .clinic import ClinicHandler
        from .event import EventHandler

        self.patient = PatientHandler(self)
        self.appointment = AppointmentHandler(self)
        self.document = DocumentHandler(self)
        self.edi = EDIHandler(self)
        self.clinic = ClinicHandler(self)
        self.event = EventHandler(self)

    def start_application(self):
        """
        Starts the application using the specified path.
        """
        os.startfile(self.app_path)

    def login(self):
        """
        Logs into the application by entering the username and password.
        Checks if the login window is open and ready.
        Checks if the main window is opened and ready.
        """
        self.app_window = self.wait_for_control(
            auto.WindowControl,
            {'AutomationId': 'FormLogin'},
            search_depth=3,
            timeout=60
        )
        self.app_window.SetFocus()

        username_box = self.app_window.EditControl(AutomationId="TextLogin")
        username_box.SendKeys(text=self.username)

        password_box = self.app_window.EditControl(AutomationId="TextPwd")
        password_box.SendKeys(text=self.password)

        login_button = self.app_window.PaneControl(AutomationId="ButtonLogin")
        login_button.SetFocus()
        login_button.SendKeys('{ENTER}')

        self.app_window = self.wait_for_control(
            auto.WindowControl,
            {'AutomationId': 'FormFront'},
            search_depth=2,
            timeout=60
        )

    def open_sub_tab(self, sub_tab_name: str):
        """
        Opens a specific sub-tab in the patient's main card.

        Args:
            sub_tab_name (str): The name of the sub-tab to open (e.g., "Dokumenter").
        """
        sub_tab_button = self.app_window.TabItemControl(Name=sub_tab_name)
        is_sub_tab_selected = sub_tab_button.GetPattern(10010).IsSelected

        if not is_sub_tab_selected:
            sub_tab_button.SetFocus()
            sub_tab_button.SendKeys('{ENTER}')

    def open_tab(self, tab_name: str):
        """
        Opens a specific tab in the patient's main card.
        Poosibly functionality on other parts of Solteq with tabs as well.

        Args:
            tab_name (str): The name of the tab to open (e.g., "Frit valg").
        """
        match tab_name:
            case "Stamkort":
                tab_name_modified = "S&tamkort"
            case "Fritvalg":
                tab_name_modified = "F&ritvalg"
            case "Journal":
                tab_name_modified = "&Journal"
            case "Oversigt":
                tab_name_modified = "O&versigt"
            case _:
                tab_name_modified = tab_name

        tab_button = self.find_element_by_property(
            control=self.app_window,
            control_type=auto.ControlType.TabItemControl,
            name=tab_name_modified
        )
        is_tab_selected = tab_button.GetPattern(10010).IsSelected

        if not is_tab_selected:
            tab_button.SetFocus()
            tab_button.SendKeys('{ENTER}')
