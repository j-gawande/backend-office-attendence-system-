# HRMS Lite – Backend (FastAPI)

This folder contains the backend API for HRMS Lite, a lightweight Human Resource Management System. The backend exposes RESTful endpoints for managing employees and tracking attendance and persists data in a MySQL database.

---

## Tech Stack

- **Language**: Python 3.8+
- **Framework**: FastAPI
- **Database**: MySQL
- **ORM**: SQLAlchemy
- **Validation**: Pydantic
- **Server**: Uvicorn
- **Config**: Environment variables via `.env`

---

## Data Model

### Employees

- `id` (int, auto-increment, primary key, internal)
- `employee_id` (string, user-entered unique Employee ID)
- `full_name` (string)
- `email` (string, unique, valid email format)
- `department` (string)

### Attendance

- `id` (int, auto-increment, primary key)
- `employee_id` (string, foreign key referencing `employees.employee_id`)
- `date` (date)
- `is_present` (boolean; `true` = Present, `false` = Absent)
- Unique constraint on (`employee_id`, `date`)

---

## Steps to Run the Backend Locally

### 1. Prerequisites

- Python 3.8 or higher
- MySQL Server running locally
- pip (Python package manager)

### 2. Install Dependencies

  From the `backend` directory:

  ```bash
  cd backend
  python -m venv venv
  venv\Scripts\activate    # On Windows
  # source venv/bin/activate  # On Linux/macOS

  python -m pip install -r requirements.txt
  ```

### 3. Configure the Database

Create the hrms_lite database and tables in MySQL:

```sql
CREATE DATABASE hrms_lite;
USE hrms_lite;

CREATE TABLE employees (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  employee_id  VARCHAR(50)    NOT NULL UNIQUE,
  full_name    VARCHAR(100)   NOT NULL,
  email        VARCHAR(150)   NOT NULL UNIQUE,
  department   VARCHAR(100)   NOT NULL
);

CREATE TABLE attendance (
  id           INT AUTO_INCREMENT PRIMARY KEY,
  employee_id  VARCHAR(50)    NOT NULL,
  date         DATE           NOT NULL,
  is_present   BOOLEAN        NOT NULL DEFAULT TRUE,
  CONSTRAINT fk_attendance_employee
    FOREIGN KEY (employee_id) REFERENCES employees(employee_id)
    ON DELETE CASCADE,
  CONSTRAINT uc_employee_date UNIQUE (employee_id, date)
);
```

### 4. Environment Variables

Create a `.env` file in the `backend` directory:

```env
DB_USER=root
DB_PASSWORD=your_password_here
DB_HOST=localhost
DB_PORT=3306
DB_NAME=hrms_lite
```
The application builds a MySQL connection URL from these values.

### 5. Run the Backend

From the backend folder with the virtual environment activated:

#### Development Mode

```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at:
- **API**: http://localhost:8000
- **Interactive API Docs (Swagger UI)**: http://localhost:8000/docs
- **Alternative API Docs (ReDoc)**: http://localhost:8000/redoc

#### Production Mode

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Core API Endpoints

### Base URL
All endpoints are prefixed with `/api`

### Employee Endpoints

#### Create Employee
```http
POST /api/employees
Content-Type: application/json

{
  "employee_id": "W531959",
  "full_name": "Devashish",
  "email": "devashish@example.com",
  "department": "Engineering"
}
```

**Response:**
- `201 Created`: Employee created successfully
- `400 Bad Request`: Invalid email or missing fields
- `409 Conflict`: Email already exists

#### List All Employees
```http
GET /api/employees
```

**Response:** Array of all employees

#### Get Single Employee
```http
GET /api/employees/{employee_id}
```

**Response:**
- `200 OK`: Employee details
- `404 Not Found`: Employee does not exist

#### Delete Employee
```http
DELETE /api/employees/{employee_id}
```

**Response:**
- `204 No Content`: Employee deleted successfully (cascades to attendance records)
- `404 Not Found`: Employee does not exist

### Attendance Endpoints

#### Mark Attendance
```http
POST /api/attendance
Content-Type: application/json

{
  "employee_id": "W531959",
  "date": "2026-01-17",
  "is_present": true
}
```

**Response:**
- `201 Created`: Attendance record created
- `400 Bad Request`: Invalid status/date format or missing fields
- `404 Not Found`: Employee does not exist
- `409 Conflict`: Attendance for that date already exists

#### List All Attendance Records
```http
GET /api/attendance?date=2026-01-17&employee_id=1
```

**Query Parameters (optional):**
- `date`: Filter by specific date (YYYY-MM-DD)
- `employee_id`: Filter by employee ID

#### Get Employee Attendance
```http
GET /api/employees/{employee_id}/attendance?start_date=2026-01-01&end_date=2026-01-31
```

**Query Parameters (optional):**
- `start_date`: Start date for filtering (YYYY-MM-DD)
- `end_date`: End date for filtering (YYYY-MM-DD)

#### Get Attendance Summary
```http
GET /api/employees/{employee_id}/attendance/summary
```

**Response:**
```json
{
  "employee_id": "W531959",
  "full_name": "Devashish",
  "total_present_days": 20,
  "total_absent_days": 3
}
```

---

## Assumptions and Limitations  

* No authentication: All endpoints are open; this is intentional for the assignment.

* Single tenant: No concept of multiple organizations/companies.

* Simple validation:

  * Email must be unique and syntactically valid.

  * Employee ID must be user-entered and unique.

* No migrations: Database schema changes are assumed to be done manually (no Alembic scripts).

* MySQL only: Configuration is built for MySQL; other databases would need adjustments.
