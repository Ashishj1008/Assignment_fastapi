from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import mysql.connector

app = FastAPI()

# Database configuration
db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Ashish@987456123",
    database="school_db"
)


# Models
class Teacher(BaseModel):
    id: int
    name: str


class Student(BaseModel):
    id: int
    name: str
    teacher_id: int


# API endpoints
@app.get("/")
def hello_world():
    return "Hello World"


@app.get("/teachers/{teacher_id}")
def get_teacher(teacher_id: int):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM teacher WHERE id = %s", (teacher_id,))
    teacher = cursor.fetchone()

    if teacher:
        return {"id": teacher[0], "name": teacher[1]}
    else:
        raise HTTPException(status_code=404, detail="Teacher not found")


@app.get("/students/{student_id}")
def get_student(student_id: int):
    cursor = db.cursor()
    cursor.execute("SELECT * FROM student WHERE id = %s", (student_id,))
    student = cursor.fetchone()

    if student:
        return {"id": student[0], "name": student[1], "teacher_id": student[2]}
    else:
        raise HTTPException(status_code=404, detail="Student not found")


@app.post("/teachers")
def create_teacher(teacher: Teacher):
    cursor = db.cursor()
    cursor.execute("INSERT INTO teacher (id, name) VALUES (%s, %s)", (teacher.id, teacher.name))
    db.commit()
    return {"message": "Teacher created"}


@app.post("/students")
def create_student(student: Student):
    cursor = db.cursor()
    cursor.execute("INSERT INTO student (id, name, teacher_id) VALUES (%s, %s, %s)",
                   (student.id, student.name, student.teacher_id))
    db.commit()
    return {"message": "Student created"}


@app.put("/students/{student_id}")
def assign_teacher(student_id: int, teacher_id: int):
    cursor = db.cursor()
    cursor.execute("UPDATE student SET teacher_id = %s WHERE id = %s", (teacher_id, student_id))
    db.commit()
    return {"message": "Student assigned to teacher"}


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    cursor = db.cursor()
    cursor.execute("DELETE FROM student WHERE id = %s", (student_id,))
    db.commit()
    return {"message": "Student deleted"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, port=6500, log_level="debug")
