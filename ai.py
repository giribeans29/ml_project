import os
from dotenv import load_dotenv, find_dotenv
import requests
from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv(find_dotenv())

os.environ["GOOGLE_API_KEY"] = os.getenv("API_KEY")


@tool
def lookup_patient(first_name: str, last_name: str, dob: str) -> dict:
    """Return the json input and json output of this function"""

    response = requests.post(
        "http://127.0.0.1:8000/patient_lookup/",
        json={
            "first_name": first_name,
            "last_name": last_name,
            "dob": dob,
        },
    )

    return response.json()

@tool
def doctor_availability(spclity: str, day_of_week: str, duration: int) -> dict:
    """Accept the input and Return the output"""

    response = requests.post(
        "http://127.0.0.1:8000/doctors/availability/",
        json={
            "spclity":spclity,
            "day_of_week":day_of_week,
            "duration":duration
        },
    )

    return response.json()

@tool
def book_appointments(patient_id: int, doc_id: int, time_slot: str) -> dict:
    """perform the action based on the input given"""

    response = requests.post(
        "http://127.0.0.1:8000/appointments/book/",
        json={
            "patient_id":patient_id,
            "doc_id":doc_id,
            "time_slot":time_slot
        },
    )

    return response.json()


agent = create_agent(
    model="google_genai:gemini-2.5-flash-lite",
    tools=[lookup_patient,doctor_availability,book_appointments],
    system_prompt="""
You are a medical receptionist.

First, you must ask the patient's name and specifically mention the first name, last name and
the date of birth of the patient. After that you take that and call the lookup_patient tool.

Based on the output, if the patient is new, ask what speciality of doctor and what time slot does the patient want.
based upon the response call the doctor_availabilty tool and then compare with the available doctors and present the available doctors
and confirm it with the patient.

Once we doctor and everything is confirmed, we will call the tool book_appointments
and update the record. 
"""
)