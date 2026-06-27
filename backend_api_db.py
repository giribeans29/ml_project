from fastapi import FastAPI, Path
import sqlite3
from pydantic import BaseModel
import sqlalchemy
from langchain.agents import create_agent
from langchain_core.tools import tool
import requests
from langchain_google_genai import ChatGoogleGenerativeAI

# conn1 =  sqlite3.connect('patients.db')
# conn2 = sqlite3.connect('doctors.db')

# # c1 = conn1.cursor()
# c2 = conn2.cursor()

app = FastAPI()

# lookup - firstname, lastname, dob, status, returning, patient_id
# doc availanlity - accepts speciality, day, duration returns with a list of available slots
# appointments book - accepts patient_id, doc_id, time_slot and updates the db as booked
class patient(BaseModel):
    first_name: str
    last_name: str
    dob: str
    patient_id: int
    status: str

class doc(BaseModel):
    doc_id: int
    spclity: str
    availability: str
    day_avail: str
    duration: int
    time: str

# c2.execute("""
#            ALTER table doctors_list ADD COLUMN booked text
# """)
@app.post("/patient_lookup/{first_name}/{last_name}/{dob}")
def patient_lookup(
    first_name: str,
    last_name: str,
    dob: str
):
    conn1 = sqlite3.connect("patients.db")
    c1 = conn1.cursor()

    query = "SELECT * FROM patients_list WHERE first_name = ? AND last_name = ? AND dob = ?"

    c1.execute(query, (first_name, last_name, dob))
    item = c1.fetchone()

    conn1.close()

    if item is not None:
         return {
        "status": "returning",
        "patient_id": item[4]
    }
    else:
        return {
        "status": "new",
        "patient_id": None
    }

@app.post("/doctors/availability/")
def get_avail_list(speciality: str,
                   day_avail: str,
                   duration: int):
    conn2 = sqlite3.connect('doctors.db')
    c2 = conn2.cursor()
    query = "SELECT * FROM doctors_list WHERE spclity = ? AND day_avail = ? AND duration = ? AND booked = ?"
    c2.execute(query, (speciality, day_avail, duration, 'No'))
    items = c2.fetchall()
    conn2.close()
    return items

@app.post("/appointments/book/")
def appointment_booking(
    patient_id: int,
    doc_id: int,
    time_slot: str
):
    conn = sqlite3.connect("doctors.db")
    c = conn.cursor()
    c.execute(
        "SELECT booked FROM doctors_list WHERE doc_id=? AND time_slot=?",
        (doc_id, time_slot)
    )
    slot = c.fetchone()
    if slot is None:
        conn.close()
        return {"message": "Slot not found"}
    if slot[0] == "Yes":
        conn.close()
        return {"message": "Slot already booked"}
    c.execute(
        """
        UPDATE doctors_list
        SET booked='Yes'
        WHERE doc_id=? AND time_slot=?
        """,
        (doc_id, time_slot)
    )
    conn.commit()
    conn.close()
    return {"message": "Appointment booked successfully"}



# agent = create_agent(
#     model="google_genai:gemini-3.5-flash",
#     tools=tool
# )


# @tool







