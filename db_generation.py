from faker import Faker
import pandas as pd
import sqlite3
import random

conn1 = sqlite3.connect("patients.db")
conn2 = sqlite3.connect("doctors.db")

fake = Faker()

patients = []
for _ in range(1,51):
    patients.append({
        "patient_id": fake.numerify('####'),
        "first_name":fake.first_name(),
        "last_name":fake.last_name(),
        "dob":fake.date_of_birth(),
        "gender":random.choice(["M","F"]),
        "phone": fake.phone_number(),
        "email":fake.email(),
        "insurance_company": random.choice(['SBI','GIG','ICICI','Xenos','NLI']),
        "member_id":fake.numerify("###"),
        "group_number": fake.numerify("#")
    })

doctors = []
for _ in range(1,11):
    doctors.append({
        "doc_id":fake.numerify("###"),
        "doctor_name":fake.name(),
        "spclity":random.choice(['Orthopaedics','GeneralMedicine','Cardiology','Nephrology','Pulmonology','Oncology']),
        "day_of_week": fake.day_of_week(),
        "time_slot": random.choice( ["09:00 AM","10:00 AM","11:00 AM","01:00 PM","02:00 PM","03:00 PM"]),
        "is_booked": random.choice([True,False])
    })

df_patients = pd.DataFrame(patients)
df_doctors = pd.DataFrame(doctors)

df_patients.to_csv("patients_list.csv", index=False)
df_doctors.to_csv("doctor_schedule.csv", index=False)
df_doctors.to_sql(name="patients", index=False,con=conn1)
df_patients.to_sql("doctor_Schedule", index=False, con=conn2)