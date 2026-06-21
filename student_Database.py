from fastapi import FastAPI, Path
from typing import Optional
from pydantic import BaseModel
import sqlite3

conn  = sqlite3.connect('student.db')
c = conn.cursor()
app = FastAPI()

# c.execute(""" CREATE TABLE student_list (
#           name text,
#           section integer
#           )
# """)
students = [('Ron',3),
            ('Bob', 4),
            ('Shawn', 5)]
# c.executemany("INSERT INTO student_list VALUES (?,?)",students)

class Student(BaseModel):
    name:str
    section: int

class updatestudent(BaseModel):
    name: Optional[str] = None
    section: Optional[int] = None

@app.get("/get-student/{Section}")
def get_student(Section: int = Path(description="The section of student", gt=0)):
    conn = sqlite3.connect("student.db")
    c = conn.cursor()
    query = "SELECT rowid, * FROM student_list WHERE Section = ?"
    
    c.execute(query, (Section,))
    item = c.fetchall()

    c.close()
    conn.close()

    return {"item": item}

@app.get("/student-list/")
def full_list():
    conn = sqlite3.connect("student.db")
    c = conn.cursor()
    c.execute("SELECT * FROM student_list")
    items = c.fetchall()
    conn.close()

    return {"students": items}

@app.post("/create-student")
def create_student(student: Student):
    conn = sqlite3.connect("student.db")
    c = conn.cursor()
    c.execute(
        "INSERT INTO student_list VALUES (?, ?)",
        (student.name, student.section)
    )
    conn.commit()
    c.close()
    conn.close()
    return {
        "message": "Student added successfully",
        "student": student
    }

@app.put("/update-student")
def update_student(section: int, student: updatestudent):
    conn = sqlite3.connect("student.db")
    c = conn.cursor()
    if student.name is not None:
        query = "UPDATE student_list SET name = ? WHERE section = ?"
        c.execute(query, (student.name, section))
    if student.section is not None:
        query = "UPDATE student_list SET section = ? WHERE section = ?"
        c.execute(query, (student.section, section))
    conn.commit()
    conn.close()
    return {"message": "Student updated successfully"}