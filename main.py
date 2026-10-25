from contextlib import asynccontextmanager
from datetime import date
import sqlite3
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field

DB_PATH = "students.db"


def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def initialize_database():
    with get_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                student_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date_of_birth TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                course TEXT,
                address TEXT,
                enrollment_date TEXT
            )
        """)
        conn.commit()


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="Students Database CRUD API",
    description="A student record management API built with FastAPI and SQLite.",
    version="1.0.0",
    lifespan=lifespan,
)


class StudentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    date_of_birth: date
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=250)
    enrollment_date: Optional[date] = None


class StudentUpdate(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=100)
    date_of_birth: Optional[date] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = Field(default=None, max_length=20)
    course: Optional[str] = Field(default=None, max_length=100)
    address: Optional[str] = Field(default=None, max_length=250)
    enrollment_date: Optional[date] = None


def row_to_dict(row):
    return dict(row) if row else None


@app.get("/")
def home():
    return {
        "message": "Students Database CRUD API is running",
        "documentation": "/docs",
        "endpoints": ["/students", "/students/{student_id}"],
    }


@app.post("/students", status_code=201)
def create_student(student: StudentCreate):
    data = student.model_dump()
    values = {
        key: value.isoformat() if isinstance(value, date) else value
        for key, value in data.items()
    }

    with get_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO students
            (name, date_of_birth, email, phone, course, address, enrollment_date)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            values["name"].strip(),
            values["date_of_birth"],
            values["email"],
            values["phone"],
            values["course"],
            values["address"],
            values["enrollment_date"],
        ))
        conn.commit()
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (cursor.lastrowid,)
        ).fetchone()
    return row_to_dict(row)


@app.get("/students")
def list_students(
    name: Optional[str] = Query(default=None, description="Filter by part of a student's name"),
    course: Optional[str] = Query(default=None, description="Filter by course"),
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
):
    sql = "SELECT * FROM students WHERE 1=1"
    params = []
    if name:
        sql += " AND name LIKE ?"
        params.append(f"%{name}%")
    if course:
        sql += " AND course LIKE ?"
        params.append(f"%{course}%")
    sql += " ORDER BY student_id LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    with get_connection() as conn:
        rows = conn.execute(sql, params).fetchall()
    return [row_to_dict(row) for row in rows]


@app.get("/students/{student_id}")
def get_student(student_id: int):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
    if row is None:
        raise HTTPException(status_code=404, detail="Student not found")
    return row_to_dict(row)


@app.put("/students/{student_id}")
def update_student(student_id: int, student: StudentUpdate):
    updates = student.model_dump(exclude_unset=True)
    if not updates:
        raise HTTPException(status_code=400, detail="Provide at least one field to update")

    allowed_fields = {
        "name", "date_of_birth", "email", "phone", "course", "address", "enrollment_date"
    }
    assignments = []
    values = []
    for key, value in updates.items():
        if key not in allowed_fields:
            continue
        if isinstance(value, date):
            value = value.isoformat()
        if key == "name" and value is not None:
            value = value.strip()
        assignments.append(f"{key} = ?")
        values.append(value)

    values.append(student_id)
    with get_connection() as conn:
        existing = conn.execute(
            "SELECT student_id FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
        if existing is None:
            raise HTTPException(status_code=404, detail="Student not found")
        conn.execute(
            f"UPDATE students SET {', '.join(assignments)} WHERE student_id = ?", values
        )
        conn.commit()
        row = conn.execute(
            "SELECT * FROM students WHERE student_id = ?", (student_id,)
        ).fetchone()
    return row_to_dict(row)


@app.delete("/students/{student_id}")
def delete_student(student_id: int):
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM students WHERE student_id = ?", (student_id,)
        )
        conn.commit()
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Student not found")
    return {"message": "Student deleted successfully", "student_id": student_id}
