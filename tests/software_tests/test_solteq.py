"""Module to test some Solteq Tand functions

Tested functionalities:

    - Open Solteq program:
        Function:
            SolteqTandApp.start_application
        Assertion:
            TMTand.exe in running processes
        Dependencies:
            None

    - Login to Solteq with SvcRpaMBU001:
        Function:
            SolteqTandApp.login
        Assertion:
            Main window title starts with "Hovedvindue - "
        Dependencies:
            test_open

    - Open patient window:
        Function:
            SolteqTandApp.open_patient
        Assertion:
            Window title starts with patient SSN
        Dependencies:
            test_login

    - Close patient window:
        Function:
            SolteqTandApp.close_patient_window
        Assertion:
            Window title returns to "Hovedvindue - "
        Dependencies:
            test_open_patient

    - Open aftalebog from main menu:
        Function:
            SolteqTandApp.open_from_main_menu("Aftalebog")
        Assertion:
            Window title starts with "Aftalebog - "
        Dependencies:
            test_login

    - Close general window:
        Function:
            SolteqTandApp.close_window
        Assertion:
            Window no longer exists
            TMTand.exe not in processes if main window closed
        Dependencies:
            test_open_patient or test_open_aftalebog

    Requirements:
        SvcRpaMBU001 in env variables with password as value
        SolteqTandTestPatient in env variables with SSN as value

    Further descrption:
        After each test, the app closes down and runs initial steps like open_app and login to allow for the testing of the specific function.


"""
import os
import subprocess as sp

import pytest
import psutil
from pytest_dependency import depends

from mbu_dev_shared_components.solteqtand.application.app_handler import SolteqTandApp


SOLTEQ_APP = SolteqTandApp(
    app_path=R"C:\Program Files (x86)\TM Care\TM Tand\TMTand.exe",
    username="SvcRpaMBU001",
    password=os.getenv("SvcRpaMBU001"),
)
SSN = os.getenv("SolteqTandTestPatient")


def depends_or(request, other, scope='module'):
    """Function to check dependency tests with or condition"""
    item = request.node
    for o in other:
        try:
            depends(request, [o], scope)
        except pytest.skip.Exception:
            continue
        else:
            return
    pytest.skip(f"{item.name} depends on any of {', '.join(other)}")


@pytest.fixture(scope="function", autouse=True)
def ensure_app_cleanup():
    """Ensure Solteq Tand app is closed after all tests"""
    yield  # Run all tests
    for proc in psutil.process_iter(['pid', 'name']):
        if proc.info['name'] == 'TMTand.exe':
            proc.terminate()
            try:
                proc.wait(timeout=5)
            except psutil.TimeoutExpired:
                proc.kill()


@pytest.mark.dependency()
def test_open():
    """Tests whether app opens"""
    SOLTEQ_APP.start_application()

    # Assert that program is in running processes
    list_processes = ['wmic', 'process', 'get', 'description']
    assert 'TMTand.exe' in sp.check_output(list_processes).strip().decode()


@pytest.mark.dependency(depends=["test_open"])
def test_login():
    """Test whether app handles login"""
    SOLTEQ_APP.start_application()
    SOLTEQ_APP.login()

    # Assert that window name starts with Hovedvindue
    window_name = "Hovedvindue - "
    assert SOLTEQ_APP.app_window.Name.upper()[:len(window_name)] == window_name.upper()


@pytest.mark.dependency(depends=["test_login"])
def test_open_patient():
    """Test whether app can open patient window"""
    SOLTEQ_APP.start_application()
    SOLTEQ_APP.login()
    SOLTEQ_APP.open_patient(ssn=SSN)

    # Assert that window name matches inputted SSN
    assert SOLTEQ_APP.app_window.Name.replace("-", "")[:len(SSN)] == SSN


@pytest.mark.dependency(depends=["test_open_patient"])
def test_close_patient():
    """Test whether app can close patient window"""
    SOLTEQ_APP.start_application()
    SOLTEQ_APP.login()
    SOLTEQ_APP.open_patient(ssn=SSN)
    SOLTEQ_APP.close_patient_window()

    # Assert that app returns to hovedvindue
    window_name = "Hovedvindue - "
    assert SOLTEQ_APP.app_window.Name.upper()[:len(window_name)] == window_name.upper()


@pytest.mark.dependency(depends=["test_login"])
def test_open_aftalebog():
    """Test whether app can open aftalebog"""
    SOLTEQ_APP.start_application()
    SOLTEQ_APP.login()
    SOLTEQ_APP.open_from_main_menu("Aftalebog")

    # Assert that window name is "Aftalebog - "
    window_name = "Aftalebog - "
    assert SOLTEQ_APP.app_window.Name.upper()[:len(window_name)] == window_name.upper()


@pytest.mark.dependency()
def test_close_window(request):
    """Tests ability to close window with CTRL+F4"""
    if request:
        depends_or(request, ["test_open_patient", "test_open_aftalebog"])
    SOLTEQ_APP.start_application()
    SOLTEQ_APP.login()
    for method, param in {SOLTEQ_APP.open_from_main_menu: "Aftalebog", SOLTEQ_APP.open_patient: SSN}.items():
        try:
            method(param)
            break
        except Exception:
            pass

    # Assert that window no longer exists
    prev_window = SOLTEQ_APP.app_window
    SOLTEQ_APP.close_window(SOLTEQ_APP.app_window)
    assert not prev_window.Exists()
    assert SOLTEQ_APP.app_window.Name.startswith("Hovedvindue")

    # Close main window after closing Aftalebog and patient assert window gone and TMTand.exe closed
    SOLTEQ_APP.close_window(SOLTEQ_APP.app_window)
    assert not SOLTEQ_APP.app_window.Exists()
    assert 'TMTand.exe' not in [p.info['name'] for p in psutil.process_iter(['name'])]


if __name__ == '__main__':
    test_close_window(None)
