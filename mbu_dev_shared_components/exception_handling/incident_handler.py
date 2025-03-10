"""Test the ServiceNow API."""

import requests


INCIDENT_SYS_ID = ""

PROD_INSTANCE = "aarhuskommune"
TEST_INSTANCE = "aarhuskommunedev"

USERNAME = ""
PASSWORD = ""

CORRELATION_ID = ""
CONTACT_TYPE = "integration"
SHORT_DESCRIPTION = ""
DESCRIPTION = ""
CALLER = ""  # Instance Creator Caller
BUSINESS_SERVICE = ""  # What should this be?
SERVICE_OFFERING = ""  # What should this be?
ASSIGNMENT_GROUP = "bae93519973586504138f286f053afac"  # MBU Proces Udvikling Assignment Group


def post_incident(message, error, queue_element):
    """POST a CSM case by sys_id or case number."""

    print("inside post_incident() function ...")

    print("message:", message)
    print("error:", error)
    print("queue_element:", queue_element)

    url = f"https://{TEST_INSTANCE}.service-now.com/api/buno/databus/incident/{INCIDENT_SYS_ID}"

    incident_data = {
        "correlationId": "",
        "contactType": F"{CONTACT_TYPE}",
        "shortDescription": F"{SHORT_DESCRIPTION}",
        "description": F"{DESCRIPTION}",
        "caller": F"{CALLER}",
        "businessService": "",
        "serviceOffering": "",
        "assignmentGroup": F"{CALLER}",
        "assignedTo": ""
    }

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }

    response = requests.post(url, json=incident_data, headers=headers, auth=(USERNAME, PASSWORD))

    print()
    print("Response Status Code:", response.status_code)
    print("Response Text:", response.text)

    if response.status_code == 200:
        return response.json().get("result", {})

    else:
        print(f"Error {response.status_code}: {response.text}")

        return None


if __name__ == "__main__":
    print("testing post_incident ...")

    test_error_message = ""

    test_message = ""
    test_error = ""
    test_queue_element = ""

    incident = post_incident(test_message, test_error, test_queue_element)

    print(f"printing incident: {incident}")
