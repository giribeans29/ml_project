from fastapi import FastAPI, Path
import sqlite3
from pydantic import BaseModel
import sqlalchemy
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

# c2.execute("""
#            CREATE TABLE doctors_list (
#            doc_id integer
#            spclity text,
#            day_avail text,
#            duration integer
#            )
# """)
@app.get("/patient_lookup/{first_name}/{last_name}/{dob}")
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

    if item is None:
         return {
        "status": item[3],
        "patient_id": item[4]
    }
    else:
        return {
        "status": item[3],
        "patient_id": "null"
    }

@app.get("/doctors/availability/")
def get_avail_list(speciality: str,
                   day_avail: str,
                   duration: int):
    conn2 = sqlite3.connect('doctors.db')
    c2 = conn2.cursor()
    query = "SELECT * FROM doctors_list WHERE spclity = ? AND day_avail = ? AND duration = ?"
    c2.execute(query, (speciality, day_avail, duration))
    items = c2.fetchall()
    return items

    