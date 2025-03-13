""" this is the main script """

import time
import os
import json
import urllib.parse

from io import BytesIO
from sqlalchemy import create_engine

import openpyxl
import pandas as pd

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from itk_dev_shared_components.smtp import smtp_util


def main(os2_webform_id, orchestrator_connection):
    """
    this is the main function
    """

    sql_server_connection_string = orchestrator_connection.get_constant("DbConnectionString").value

    print("Fetching data ...")
    data = get_forms_data(os2_webform_id, sql_server_connection_string)

    print("Creating Excel file ...")
    output_dir = os.path.join("C:\\", "tmp", "FormsExport")
    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.join(output_dir, "form_data.xlsx")
    pd.DataFrame(data).to_excel(filename, index=False)

    print(f"Excel file saved at: {filename}")

    print("Sending excel file to specified email receiver ...")
    send_excel_file(orchestrator_connection, filename)

    time.sleep(5)
    print("Cleaning up Excel file ...")
    if os.path.exists(filename):
        os.remove(filename)

        print(f"Deleted: {filename}")

    return data


def get_forms_data(form_type: str, conn_string: str) -> list[dict]:
    """
    Retrieve form_data['data'] for all matching submissions and export to Excel.
    """
    query = """
        SELECT
            form_id,
            form_data,
            CAST(form_submitted_date AS datetime) AS form_submitted_date
        FROM [RPA].[journalizing].[Forms]
        WHERE form_type = ?
        ORDER BY form_submitted_date DESC
    """

    # Create SQLAlchemy engine
    encoded_conn_str = urllib.parse.quote_plus(conn_string)
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={encoded_conn_str}")

    # Run query
    df = pd.read_sql(query, engine, params=(form_type,))

    if df.empty:
        print("No submissions found for the given form type.")

        return []

    # Extract the form_data["data"] dicts
    extracted_data = [
        json.loads(row["form_data"])["data"] for _, row in df.iterrows()
    ]

    return extracted_data


def send_excel_file(orchestrator_connection: OrchestratorConnection, filepath: str):
    """Function to send email with manual list"""

    filename = filepath.split("\\")[-1]

    # start_date, end_date = get_start_end_dates()
    # start_date = start_date.strftime("%d.%m.%Y")
    # end_date = end_date.strftime("%d.%m.%Y")

    # Read excel file into BytesIO object
    wb = openpyxl.load_workbook(filepath)

    excel_buffer = BytesIO()

    wb.save(excel_buffer)

    excel_buffer.seek(0)

    proc_args = json.loads(orchestrator_connection.process_arguments)

    email_recipient = proc_args["email_recipient"]

    email_sender = orchestrator_connection.get_constant("e-mail_noreply").value

    email_subject = "Submissions for test periode"

    email_body = proc_args["email_body"]

    attachments = [smtp_util.EmailAttachment(
        file=excel_buffer, file_name=filename
    )]

    smtp_util.send_email(
        receiver=email_recipient,
        sender=email_sender,
        subject=email_subject,
        body=email_body,
        html_body=True,
        smtp_server="smtp.adm.aarhuskommune.dk",
        smtp_port="25",
        attachments=attachments if attachments else None
    )


if __name__ == "__main__":
    print("Testing ...")

    test_webform_id = "tilmelding_til_modersmaalsunderv"

    test_orchestrator_connection = OrchestratorConnection(
        process_name="test process name",
        connection_string=os.getenv("ORCHESTRATOR_CONNECTION_STRING"),
        crypto_key=os.getenv("ORCHESTRATOR_ENCRYPTION_KEY"),
        process_arguments='{"email_recipient": "dadj@aarhus.dk", "email_body": "<p>This is a test body.</p>"}'
    )

    main(test_webform_id, test_orchestrator_connection)
