import os
from dotenv import load_dotenv
import requests

from langchain.agents import create_agent
from langchain_core.tools import tool

load_dotenv()

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


agent = create_agent(
    model="google_genai:gemini-2.5-flash-lite",
    tools=[lookup_patient],
    system_prompt="""
You are a medical receptionist.

Whenever the user gives their first name, last name and their date of birth,
use your lookup tool. Once you get the tool's JSON response, output that exact 
JSON object as your final response text. Do not add any conversational filler.
"""
)



user = input("\nYou: ")

response = agent.invoke(
    {
        "messages": [
                {
                    "role": "user",
                    "content": user
                }
            ]
        }
    )

print("\nAssistant:")
tool_messages = [msg.content for msg in response["messages"] if msg.type == "tool"]

if tool_messages:
    print(tool_messages[0])
else:
    print(response["messages"][-1].content)