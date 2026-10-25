# Students Database CRUD Application

A beginner-friendly backend project for managing student records using **Python, FastAPI and SQLite**.

## Features

- Create, read, update and delete student records.
- SQLite database persists records between restarts.
- Search/filter by name or course.
- Input validation using Pydantic.
- Clear 404 errors when a student does not exist.
- Interactive API documentation at `/docs`.

## Requirements

- Python 3.10 or newer
- pip

## Installation

1. Extract the project ZIP and open a terminal in the project folder.
2. Create a virtual environment (recommended):

   **Windows**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

   **macOS/Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Run the application

```bash
uvicorn main:app --reload
```

Open these URLs in your browser:

- API home: http://127.0.0.1:8000/
- Interactive API testing: http://127.0.0.1:8000/docs

The `students.db` SQLite database is created automatically when the app starts.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| POST | `/students` | Create a student |
| GET | `/students` | List students |
| GET | `/students/{student_id}` | Get one student |
| PUT | `/students/{student_id}` | Update a student |
| DELETE | `/students/{student_id}` | Delete a student |

Optional filters: `/students?name=Ravi`, `/students?course=CSE`

## Sample request: create a student

In `/docs`, open `POST /students`, click **Try it out**, and enter:

```json
{
  "name": "Ravi Kumar",
  "date_of_birth": "2005-04-15",
  "email": "ravi@example.com",
  "phone": "9000000000",
  "course": "CSE",
  "address": "Hyderabad",
  "enrollment_date": "2025-08-01"
}
```

Use dummy/sample information only. Do not upload real student personal information.

## Example update

```json
{
  "course": "Computer Science"
}
```

Submit this body to `PUT /students/1`.

## GitHub submission

1. Create a new GitHub repository.
2. Upload `main.py`, `requirements.txt`, `README.md`, and `.gitignore`.
3. Do not upload `.venv/`, `students.db`, passwords, secrets, or real personal data.
4. Copy the repository URL and submit it to your trainer.

## Project architecture

- **FastAPI** receives HTTP requests and returns JSON responses.
- **Pydantic** validates request data.
- **SQLite** stores student records in a local database file.
- **Uvicorn** runs the API server.

## Optional extension

The assignment mentions a local AI extension with Ollama. It is not included in this starter version; finish and test all CRUD operations first.
