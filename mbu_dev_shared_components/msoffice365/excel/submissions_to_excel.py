""" this is the main script """

import os
import json
import urllib.parse

from datetime import datetime, timedelta
from io import BytesIO
from sqlalchemy import create_engine

import openpyxl
import pandas as pd

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from itk_dev_shared_components.smtp import smtp_util


def main(orchestrator_connection: OrchestratorConnection):
    """
    this is the main function
    """

    sql_server_connection_string = orchestrator_connection.get_constant("DbConnectionString").value

    proc_args = json.loads(orchestrator_connection.process_arguments)

    os2_webform_id = proc_args["os2_webform_id"]

    end_date = datetime.today().date() - timedelta(days=1)
    start_date = end_date - timedelta(weeks=proc_args["weeks_back"])

    print("Fetching data ...")
    data = get_forms_data(sql_server_connection_string, os2_webform_id, start_date, end_date)

    print("Creating Excel file ...")
    output_dir = os.path.join("C:\\", "tmp", f"{os2_webform_id}_FormsExport")
    os.makedirs(output_dir, exist_ok=True)

    filename = os.path.join(output_dir, f"form_data_{start_date}_{end_date}.xlsx")

    if os.path.exists(filename):
        print("Existing file found. Deleting it before creating a new one.")

        os.remove(filename)

    pd.DataFrame(data).to_excel(filename, index=False)

    print(f"Excel file saved at: {filename}")

    print("Sending excel file to specified email receiver ...")
    send_excel_file(os2_webform_id, orchestrator_connection, filename, start_date, end_date)

    print("Cleaning up Excel file ...")
    if os.path.exists(filename):
        os.remove(filename)

        print(f"Deleted: {filename}")

    return data


def get_forms_data(conn_string: str, form_type: str, start_date, end_date) -> list[dict]:
    """
    Retrieve form_data['data'] for all matching submissions in the past `weeks_back` weeks until yesterday.
    """

    query = """
        SELECT
            form_id,
            form_data,
            CAST(form_submitted_date AS datetime) AS form_submitted_date
        FROM
            [RPA].[journalizing].[Forms]
        WHERE
            form_type = ?
            AND CAST(form_submitted_date AS date) BETWEEN ? AND ?
        ORDER BY form_submitted_date DESC
    """

    # Create SQLAlchemy engine
    encoded_conn_str = urllib.parse.quote_plus(conn_string)
    engine = create_engine(f"mssql+pyodbc:///?odbc_connect={encoded_conn_str}")

    # Run query
    df = pd.read_sql(sql=query, con=engine, params=(form_type, start_date, end_date))

    if df.empty:
        print("No submissions found for the given form type and date range.")
        return []

    # Extract the form_data["data"] dicts
    extracted_data = [
        json.loads(row["form_data"])["data"] for _, row in df.iterrows()
    ]

    return extracted_data


def send_excel_file(os2_webform_id: str, orchestrator_connection: OrchestratorConnection, filepath: str, start_date: datetime, end_date: datetime):
    """Function to send email with submissions list"""

    filename = filepath.split("\\")[-1]

    # Read excel file into BytesIO object
    wb = openpyxl.load_workbook(filepath)

    excel_buffer = BytesIO()

    wb.save(excel_buffer)

    excel_buffer.seek(0)

    proc_args = json.loads(orchestrator_connection.process_arguments)

    email_recipient = proc_args["email_recipient"]

    email_sender = orchestrator_connection.get_constant("e-mail_noreply").value

    email_subject = f"All submissions for {os2_webform_id} from {start_date.strftime('%d-%m-%Y')} to {end_date.strftime('%d-%m-%Y')}"

    email_body = proc_args["email_body"]

    attachments = [smtp_util.EmailAttachment(file=excel_buffer, file_name=filename)]

    smtp_util.send_email(
        receiver=email_recipient,
        sender=email_sender,
        subject=email_subject,
        body=email_body,
        smtp_server="smtp.adm.aarhuskommune.dk",
        smtp_port="25",
        html_body=True,
        attachments=attachments if attachments else None
    )


if __name__ == "__main__":
    print("Testing ...")

    TEST_ORCHESTRATOR_CONNECTION = OrchestratorConnection(
        process_name="test process name",
        connection_string=os.getenv("ORCHESTRATOR_CONNECTION_STRING"),
        crypto_key=os.getenv("ORCHESTRATOR_ENCRYPTION_KEY"),
        process_arguments='{"os2_webform_id": "tilmelding_til_modersmaalsunderv", "weeks_back": 3, "email_recipient": "dadj@aarhus.dk", "email_body": "<p>This is a test body.</p>"}'
    )

    main(TEST_ORCHESTRATOR_CONNECTION)
