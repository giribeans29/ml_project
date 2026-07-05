from fastapi import FastAPI, Path
import sqlite3
from pydantic import BaseModel
from langchain.agents import create_agent
from langchain_core.tools import tool
import requests
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI

# conn1 =  sqlite3.connect('patients.db')
# conn1 = sqlite3.connect("EMR_Database.db")

# # c1 = conn1.cursor()
# c2 = conn2.cursor()

app = FastAPI()

# lookup - firstname, lastname, dob, status, returning, patient_id
# doc availanlity - accepts speciality, day, duration returns with a list of available slots
# appointments book - accepts patient_id, doc_id, time_slot and updates the db as booked
class patientlookuprequest(BaseModel):
    first_name: str
    last_name: str
    dob: str
    patient_id: int
    status: str

class doc(BaseModel):
    doc_id: int
    spclity: str
    day_avail: str
    duration: int
    time_slot: str


class BookingRequest(BaseModel):
    patient_id: int
    doc_id: int
    time_slot: str

# c2.execute("""
#            ALTER table doctors_list ADD COLUMN booked text
# """)
@app.post("/patient_lookup/")
def patient_lookup( patient: patientlookuprequest
):
    conn1 = sqlite3.connect("doctors.db")
    c1 = conn1.cursor()

    query = "SELECT * FROM patients_list WHERE first_name = ? AND last_name = ? AND dob = ?"

    c1.execute(query, (patient.first_name, patient.last_name, patient.dob))
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
def get_avail_list(doctor: doc):
    conn2 = sqlite3.connect('patients.db')
    c2 = conn2.cursor()
    query = "SELECT * FROM patients WHERE spclity = ? AND day_of_week = ? AND is_booked = ?"
    c2.execute(query, (doc.spclity, doc.day_avail, doc.duration, '0'))
    items = c2.fetchall()
    conn2.close()
    return items

@app.post("/appointments/book/")
def appointment_booking(req: BookingRequest
):
    conn = sqlite3.connect("doctors.db")
    c = conn.cursor()
    c.execute(
        "SELECT is_booked FROM patients WHERE doc_id=? AND time_slot=?",
        (req.doc_id, req.time_slot)
    )
    slot = c.fetchone()
    if slot is None:
        conn.close()
        return {"message": "Slot not found"}
    if slot[0] == "1":
        conn.close()
        return {"message": "Slot already booked"}
    c.execute(
        """
        UPDATE doctors_list
        SET is_booked='1'
        WHERE doc_id=? AND time_slot=?
        """,
        (req.doc_id, req.time_slot)
    )
    conn.commit()
    conn.close()
    return {"message": "Appointment booked successfully"}