from fastapi import FastAPI, HTTPException, Depends, Body
from sqlmodel import SQLModel, Field, create_engine, Session, select
from typing import Optional
from contextlib import asynccontextmanager

# ---------- Database ----------
DATABASE_URL = "sqlite:///students.db"
engine = create_engine(DATABASE_URL, echo=True)

class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    age: int

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Ali",
                "age": 20
            }
        }

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

# ---------- FastAPI App ----------
@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield

app = FastAPI(title="Students CRUD API", lifespan=lifespan)

# ---------- CRUD Endpoints ----------

# CREATE student
@app.post("/students/", response_model=Student)
def create_student(
    student: Student = Body(
        ...,
        example={"name": "Ali", "age": 20},
    
    ),
    session: Session = Depends(get_session)
):
    session.add(student)
    session.commit()
    session.refresh(student)
    return student

# READ all students
@app.get("/students/", response_model=list[Student])
def read_students(session: Session = Depends(get_session)):
    students = session.exec(select(Student)).all()
    return students

# READ one student
@app.get("/students/{student_id}", response_model=Student)
def read_student(student_id: int, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

# UPDATE student
@app.put("/students/{student_id}", response_model=Student)
def update_student(
    student_id: int,
    updated: Student = Body(
        ...,
        example={"name": "Ahmed", "age": 21},
    ),
    session: Session = Depends(get_session)
):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")

    student.name = updated.name
    student.age = updated.age

    session.add(student)
    session.commit()
    session.refresh(student)
    return student

# DELETE student
@app.delete("/students/{student_id}")
def delete_student(student_id: int, session: Session = Depends(get_session)):
    student = session.get(Student, student_id)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    session.delete(student)
    session.commit()
    return {"message": "Student deleted successfully"}

# Optional root
@app.get("/")
def root():
    return {"message": "Welcome! Use /docs to test the Students CRUD API"}