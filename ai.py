import os
from dotenv import load_dotenv, find_dotenv
import requests
from langchain.agents import create_agent
from langchain_core.tools import tool
from typing import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END
from langchain_core.messages import HumanMessage, SystemMessage, ToolMessage

load_dotenv(r"C:\Users\giris\Desktop\ml\venv\.env")

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

class AgentState(TypedDict):
    messages: list[BaseMessage]
    patient_status: str
    required_duration: str
    booking_confirmed: bool

agent = create_agent(
    model="google_genai:gemini-2.5-flash-lite",
    tools=[
        lookup_patient,
        doctor_availability,
        book_appointments,
    ],
    system_prompt="""
You are a medical receptionist.

Your job is to book appointments naturally.

Rules:

1. Greet the patient.
2. Ask for their first name, last name and date of birth.
3. Once you have all three, call lookup_patient.
4. If the patient is returning, remember they need a 30-minute appointment.
5. If the patient is new, remember they need a 60-minute appointment.
6. Ask for the doctor's speciality.
7. Ask for the preferred day.
8. Call doctor_availability.
9. Present the available doctors and slots.
10. Ask the patient which slot they want.
11. Call book_appointments.
12. Confirm the appointment.
"""
)

def chatbot(state: AgentState):
    result = agent.invoke(
        {
            "messages": state["messages"]
        }
    )

    state["messages"] = result["messages"]

    return state

def determine_duration(state: AgentState):

    if state["patient_status"] == "new":
        state["required_duration"] = 60
    else:
        state["required_duration"] = 30

    return state

graph_builder = StateGraph(AgentState)

graph_builder.add_node("chatbot",chatbot)
graph_builder.add_node("determine_duration", determine_duration)

graph_builder.add_edge(START, "chatbot")
graph_builder.add_edge("chatbot", "determine_duration")
graph_builder.add_edge("determine_duration", "chatbot")
graph_builder.add_edge("chatbot", END)
graph = graph_builder.compile()

state = {
    "messages": [
        SystemMessage(
            content="""
You are a medical receptionist.

Greet the patient.

Ask for:
- First name
- Last name
- Date of birth

Once you have those, call lookup_patient.

If the patient is new, they need a 60-minute appointment.
If returning, they need a 30-minute appointment.

Ask for:
- Doctor speciality
- Preferred day

Call doctor_availability.

Present the available slots.

Ask the patient to choose one.

Call book_appointments.

Confirm the booking.
"""
        )
    ],
    "patient_status": "unknown",
    "required_duration": 0,
    "booking_confirmed": False,
}
while True:

    user = input("You: ")

    state["messages"].append(
        HumanMessage(content=user)
    )

    state = chatbot(state)

    print("\nAI:", state["messages"][-1].content)

    if state["booking_confirmed"]:
        break
    if user == "exit":
        break