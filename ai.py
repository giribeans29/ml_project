from langchain.agents import create_agent
from langchain_core.tools import tool
import requests


agent = create_agent(
    model="google_genai:gemini-3.5-flash",
    tools=tool
)
