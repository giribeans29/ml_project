import os
from dotenv import load_dotenv, find_dotenv
import requests
from langchain.agents import create_agent
from langchain_core.tools import tool
from typing import TypedDict
import json
from langchain_core.messages import BaseMessage, AIMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from pprint import pprint
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
    result = response.json()
    return result

@tool
def doctor_availability(spclity: str, day_of_week: str, duration: str) -> dict:
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
def book_appointments(doc_id: str, time_slot: str) -> dict:
    """perform the action based on the input given"""

    response = requests.post(
        "http://127.0.0.1:8000/appointments/book/",
        json={
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
    model="google_genai:gemini-2.5-flash",
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

def update_state(state: AgentState):

    for msg in reversed(state["messages"]):

        if isinstance(msg, ToolMessage):

            try:
                result = json.loads(msg.content)

                # lookup_patient response
                if "status" in result:
                    state["patient_status"] = result["status"]

                # booking response
                if "message" in result:
                    if "successfully" in result["message"].lower():
                        state["booking_confirmed"] = True

            except:
                pass

    return state

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

def create_state():

    return {
        "messages": [
            SystemMessage(
                content="""
You are a medical receptionist.

Greet the patient.

Ask for:

- First name
- Last name
- Date of birth

Call lookup_patient.

Wait for the application to determine
appointment duration.

Ask for speciality.

Ask for preferred day.

Call doctor_availability.

Present slots.

Book appointment.

Confirm booking.
"""
            )
        ],
        "patient_status": "unknown",
        "required_duration": 0,
        "booking_confirmed": False,
    }

def process_message(state: AgentState, user_message: str):

    state["messages"].append(
        HumanMessage(content=user_message)
    )

    state = chatbot(state)
    state = update_state(state)
    state = determine_duration(state)

    ai_response = ""

    for msg in reversed(state["messages"]):

        if isinstance(msg, AIMessage):
            ai_response = msg.content
            break

    return state, ai_response

# while True:
#     user = input("You: ")

#     if user.lower() == "exit":
#         break

#     state["messages"].append(HumanMessage(content=user))

#     state = chatbot(state)

#     state = update_state(state)
#     state = determine_duration(state)

#     for msg in reversed(state["messages"]):
#         if isinstance(msg, AIMessage):
#             print("\nAI:", msg.text())
#             break

#     print("\nPatient Status    :", state["patient_status"])
#     print("Required Duration :", state["required_duration"])
#     print("Booking Confirmed :", state["booking_confirmed"])

#     if state["booking_confirmed"]:
#         print("\nAppointment booked successfully!")
#         break